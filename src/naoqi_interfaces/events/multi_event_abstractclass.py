from event_abstractclass import EventAbstractclass
from abc import ABCMeta
import types


class Event(list):
    def __init__(self, event_name=None, proxy_name=None, callback=None):
        super(Event, self).__init__((event_name, proxy_name, callback))

    @property
    def event_name(self):
        return self[0]

    @property
    def proxy_name(self):
        return self[1]

    @property
    def callback(self):
        return self[2]


class MultiEventAbstractclass(EventAbstractclass):
    __metaclass__ = ABCMeta

    def __init__(self, events, name=""):
        """
        Constructor for multi subscription class. This allow to subscribe to multiple events in the same class.
        
        :param events: A list of tuples `[(event_name, proxy_name, callback), ...]`
        :param name: Option argument. Can be used to define an explicit name fo the global variable that holds the 
        instance of the inheriting class. If not defined `inst.__class__.__name__+"_inst"` will be used
        """
        super(MultiEventAbstractclass, self).__init__(event=None, proxy_name=None, name=name)
        if not (isinstance(events, (list, tuple))):
            raise TypeError("events has to be a list or tuple")
        for e in events:
            if not (isinstance(e, (list, tuple, Event))):
                raise TypeError("Elements in events have to be a list, tuple, or Event")
            if not len(e) == 3:
                raise IndexError("Elements in events have to be a list, tuple, or Event of 3: (event_name, proxy_name, callback)")
            if not isinstance(e[0], str):
                raise TypeError("Event names have to be string objects.")
            if not isinstance(e[2], (types.FunctionType, types.BuiltinFunctionType, types.MethodType,
                                     types.BuiltinMethodType, types.UnboundMethodType, str)):
                raise TypeError("Callbacks have to be function objects or strings.")

        self.events = events

    def _subscribe(self):
        for e in self.events:
            self.__memory__.subscribeToEvent(
                e[0],
                self._name,
                e[2].func_name if not isinstance(e[2], str) else e[2]
            )

    def _unsubscribe(self):
        for e in self.events:
            self.__memory__.unsubscribeToEvent(
                e[0],
                self._name
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

    def init(self, glob):
        super(MultiEventAbstractclass, self).init(glob)
        for e in self.events:
            if e[1] is not None:
                self.create_proxy(e[1])
