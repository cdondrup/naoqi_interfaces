import signal
import time
import naoqi_interfaces.comms.connection as con


class EventSpinner(object):
    """
    A simple spinner that helps keeping the programme alive while reacting to events. This class also takes care of
    starting and stopping the given events and broker.

    :param globals_: The global variables of the main file, i.e. globals()
    :param broker: The active broker
    :param events: A list of events inheriting from EventAbstractclass. Can be a list of tuples,
    e.g. [(MyEvent(), [5, "test]), MyEvent2(), ...] Where the first element is the class instance and the second element
    is a list of optional arguments to the MyEvent.start method (only necessary if MyEvent overrides the start method
    from the abstract class). You are free to mix.
    """
    def __init__(self, globals_, broker, events=None):
        self.globals_ = globals_
        self.broker = broker
        self.events = events if isinstance(events, (list, tuple)) else [events] if events is not None else []
        self.__shutdown_requested = False
        self.__start()
        signal.signal(signal.SIGINT, self._signal_handler)

    def __start(self):
        for event in self.events:
            if isinstance(event, (tuple, list)):
                event[0].start(self.globals_, *(event[1] if isinstance(event[1], (tuple, list)) else [event[1]]))
            else:
                event.start(self.globals_)

    def spin(self, *args):
        """
        Blocking until Ctrl+C is received.
        :param args: Functions to be executed each iteration.
        :return:
        """
        while not self.__shutdown_requested:
            for f in args:
                f()
            time.sleep(.1)

    def _signal_handler(self, *args):
        print 'Caught Ctrl+C, stopping.'
        self.__shutdown_requested = True
        print "Executing shutdown functions."
        for event in self.events:
            event[0].stop() if isinstance(event, (tuple, list)) else event.stop()
        print "Killing broker"
        con.shutdown_broker(self.broker)
        print 'Good-bye'
