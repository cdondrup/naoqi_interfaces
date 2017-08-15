from naoqi import ALProxy, ALModule
from abc import ABCMeta, abstractmethod
import uuid
import time


class EventAbstractclass(ALModule):
    __metaclass__ = ABCMeta

    def __init__(self, event, proxy_name, name=""):
        """
        The constructor of the base abstract class.
        
        :param event: The name of the event to subscribe to, e.g. "FaceDetected"
        :param proxy_name: The name of the proxy that provides the event and has to run for it to be available, e.g. 
        "ALFaceDetection"
        :param name: Option argument. Can be used to define an explicit name fo the global variable that holds the 
        instance of the inheriting class. If not defined `inst.__class__.__name__+"_inst"` will be used
        """
        self.__event__ = event
        self._name = str(uuid.uuid4()).replace('-', '_') if name == "" else name
        self._make_global(self._name, self)
        self.__proxy_name__ = proxy_name
        self.__memory__ = None

    def _make_global(self, name, var):
        """
        Creating global variables. Helper function for the use of naoqi.
        
        :param name: The name of the global variable to be created 
        :param var: The value the variable should hold
        :return: The nwe global variable
        """
        globals()[name] = var
        return globals()[name]

    def _subscribe(self):
        """
        Subscribes to the event given during construction.
        """
        self.__memory__.subscribeToEvent(
            self.__event__,
            self._name,
            self.callback.func_name
        )

    def _unsubscribe(self):
        """
        Unsubscribes from the event given during construction.
        """
        self.__memory__.unsubscribeToEvent(
            self.__event__,
            self._name
        )

    def sync_global(self, glob):
        """
        Syncing the global variable that hold the instance of this class to the dictionary of global variables provided 
        as an argument.
        :param glob: The dictionary of global variables that should contain the variable holding the instance, i.e.
         `globals()` of the main file.
        """
        if self._name in glob:
            raise NameError("'%s' already exists in globals. New instance cannot be synced" % self._name)
        glob[self._name] = globals()[self._name]

    def get_proxy(self, proxy_name=""):
        """
        The proxy object created can either be used directly as a member variable if the name is known or via this 
        function. If no proxy_name is specified the proxy created during construction will be returned.
        
        :param proxy_name: Optional argument. If omitted, the main proxy for the event will be returned
        :return: The created proxy object to interact with 
        """
        return getattr(self, self.__proxy_name__ if proxy_name == "" else proxy_name)

    def create_proxy(self, proxy_name):
        """
        Create a proxy as a member variable. Variable name will be the same as the proxy_name. E.g. 
        `proxy_name=ALFaceDetection` will create `self.ALFaceDetection`.
        :param proxy_name: The name of the proxy as a string 
        """
        if not isinstance(proxy_name, str):
            raise TypeError("Proxy names have to be string objects.")
        while True:
            try:
                setattr(self, proxy_name, ALProxy(proxy_name))
                break
            except RuntimeError:
                print "Server '%s' could not be found. Maybe it is not running, yet. Retrying." % proxy_name
                time.sleep(1.)

    @abstractmethod
    def callback(self, *args, **kwargs):
        """
        This function is called whenever the event fires and needs to be overridden in the inheriting class
        
        :param args: List of arguments
        :param kwargs: Dictionary of keyword arguments
        """
        pass

    def initialise_proxies_and_memory(self, glob):
        """
        Syncs the necessary globals, and creates all the proxies and the memory. Called by the spinner.
        
        :param glob: The globals() of the main file 
        """
        try:
            super(EventAbstractclass, self).__init__(self._name)
        except RuntimeError:
            raise RuntimeError("The broker instance has to be created before you can create a proxy.")

        self.__memory__ = self._make_global("memory", ALProxy("ALMemory"))
        if self.__proxy_name__ is not None:
            self.create_proxy(self.__proxy_name__)

        self.sync_global(glob)

    def init(self, *args):
        """
        Override this function to call proxy functions etc. before the spinner subscribes to the event.
        """
        pass

    def start(self):
        """
        Subscribes to event given at construction
        """
        self._subscribe()

    def stop(self):
        """
        Unsubscribes from event given at construction
        """
        try:
            self._unsubscribe()
        except RuntimeError as e:
            print "Warning:", e
