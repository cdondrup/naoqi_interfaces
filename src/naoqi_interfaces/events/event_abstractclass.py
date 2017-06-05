from naoqi import ALProxy, ALModule
from abc import ABCMeta, abstractmethod


class EventAbstractclass(ALModule):
    __metaclass__ = ABCMeta

    def __init__(self, inst, event, proxy_name, name=""):
        """
        The constructor of the base abstract class.
        
        :param inst: The instance (self) of the inheriting class. 
        :param event: The name of the event to subscribe to, e.g. "FaceDetected"
        :param proxy_name: The name of the proxy that provides the event and has to run for it to be available, e.g. 
        "ALFaceDetection"
        :param name: Option argument. Can be used to define an explicit name fo the global variable that holds the 
        instance of the inheriting class. If not defined `inst.__class__.__name__+"_inst"` will be used
        """
        self.inst = inst
        self.event = event
        self.name = inst.__class__.__name__+"_inst" if name == "" else name
        self._make_global(self.name, self)
        super(EventAbstractclass, self).__init__(self.name)

        self.memory = self._make_global("memory", ALProxy("ALMemory"))
        if proxy_name is not None:
            self.create_proxy(proxy_name)
            self.proxy_name = proxy_name

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
        self.memory.subscribeToEvent(
            self.event,
            self.name,
            self.callback.func_name
        )

    def _unsubscribe(self):
        """
        Unsubscribes from the event given during construction.
        """
        self.memory.unsubscribeToEvent(
            self.event,
            self.name
        )

    def sync_global(self, glob):
        """
        Syncing the global variable that hold the instance of this class to the dictionary of global variables provided 
        as an argument.
        :param glob: The dictionary of global variables that should contain the variable hoding the instance, i.e. 
         `globals()` of the main file.
        """
        glob[self.name] = globals()[self.name]

    def get_proxy(self, proxy_name=""):
        """
        The proxy object created can either be used directly as a member variable if the name is known or via this 
        function. If no proxy_name is specified the proxy created during construction will be returned.
        
        :param proxy_name: Option argument. If omitted, the main proxy for the event will be returned
        :return: The created proxy object to interact with 
        """
        return getattr(self, self.proxy_name if proxy_name == "" else proxy_name)

    def create_proxy(self, proxy_name):
        """
        Create a proxy as a member variable. Variable name will be the same as the proxy_name. E.g. 
        `proxy_name=ALFaceDetection` will create `self.ALFaceDetection`.
        :param proxy_name: The name of the proxy as a string 
        """
        if not isinstance(proxy_name, str):
            raise TypeError("Proxy names have to be string objects.")
        setattr(self, proxy_name, ALProxy(proxy_name))

    @abstractmethod
    def callback(self, *args, **kwargs):
        """
        This function is called whenever the event fires and needs to be overridden in the inheriting class
        
        :param args: List of arguments
        :param kwargs: Dictionary of keyword arguments
        """
        pass

    def start(self, glob):
        """
        Subscribes to the event and syncs the necessary globals.
        
        :param glob: The globals() of the main file 
        """
        self.sync_global(glob)
        self._subscribe()

    def stop(self):
        """
        Unsubscribes from event given at construction
        """
        self._unsubscribe()
