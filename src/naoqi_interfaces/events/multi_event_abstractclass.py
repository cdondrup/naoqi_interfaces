from event_abstractclass import EventAbstractclass
from abc import ABCMeta
from naoqi import ALProxy
import types


class MultiEventAbstractclass(EventAbstractclass):
    __metaclass__ = ABCMeta

    def __init__(self, inst, events, name=""):
        """
        Constructor for multi subscription class. This allow to subscribe to multiple events in the same class.
        
        :param inst: The instance of the inheriting class
        :param events: A list of tuples `[(event_name, proxy_name, callback), ...]`
        :param name: Option argument. Can be used to define an explicit name fo the global variable that holds the 
        instance of the inheriting class. If not defined `inst.__class__.__name__+"_inst"` will be used
        """
        super(MultiEventAbstractclass, self).__init__(inst=inst, event=None, proxy_name=None, name=name)
        if not (isinstance(events, list) or isinstance(events, tuple)):
            raise TypeError("events has to be a list or tuple")
        for e in events:
            if not (isinstance(e, list) or isinstance(e, tuple)):
                raise TypeError("Elements in events have to be a list or tuple")
            if not len(e) == 3:
                raise IndexError("Elements in events have to be a list or tuple of 3: (event_name, proxy_name, callback)")
            if not isinstance(e[0], str):
                raise TypeError("Event names have to be string objects.")
            if not isinstance(e[2], (types.FunctionType, types.BuiltinFunctionType, types.MethodType,
                                     types.BuiltinMethodType, types.UnboundMethodType)):
                raise TypeError("Callbacks have to be function objects.")
            self.create_proxy(e[1])
        self.events = events

    def _subscribe(self):
        for e in self.events:
            self.memory.subscribeToEvent(
                e[0],
                self.name,
                e[2].func_name
            )

    def _unsubscribe(self):
        for e in self.events:
            self.memory.unsubscribeToEvent(
                e[0],
                self.name
            )

    def callback(self, *args, **kwargs):
        # Overriding this from EventAbstractclass so we do not require to have one in the inheriting class.
        return

    def get_proxy(self, proxy_name):
        """
        The proxy object created can either be used directly as a member variable if the name is known or via this 
        function.

        :param proxy_name: The name of the proxy object, e.g. ALFaceDetection
        :return: The created proxy object to interact with 
        """
        if not isinstance(proxy_name, str):
            raise TypeError("Proxy names have to be string objects.")
        return getattr(self, proxy_name)
