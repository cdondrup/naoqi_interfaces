import signal
import time
import naoqi_interfaces.comms.connection as con


class EventManager(object):
    """
    A simple manager that helps keeping the programme alive while reacting to events. This class also takes care of
    starting and stopping the given events and broker.

    :param globals_: The global variables of the main file, i.e. globals()
    :param ip: The IP to connect to. Usually the IP of the robot.
    :param port: The port to connect to, usually the port of the robot
    :param events: A list of events inheriting from EventAbstractclass. Can be a list of tuples,
    e.g. [(MyEvent(), [5, "test]), MyEvent2(), ...] Where the first element is the class instance and the second element
    is a list of optional arguments to the MyEvent.init method (only necessary if MyEvent overrides the init method
    from the abstract class). You are free to mix.
    :param target_ip: IP to listen to
    :param target_port: Port to use
    """
    def __init__(self, globals_, ip, port, events=None, target_ip="0.0.0.0", target_port=0):
        self.globals_ = globals_
        self.broker = con.create_broker(ip, port, target_ip, target_port)
        self.__on_shutdown = []
        self.events = events if isinstance(events, (list, tuple)) else [events] if events is not None else []
        self.__shutdown_requested = False
        self.__start()
        signal.signal(signal.SIGINT, self._signal_handler)

    def __start(self):
        for event in self.events:
            if isinstance(event, (tuple, list)):
                event[0].initialise_proxies_and_memory(self.globals_)
                event[0].init(*(event[1] if isinstance(event[1], (tuple, list)) else [event[1]]))
                event[0].start()
            else:
                event.initialise_proxies_and_memory(self.globals_)
                event.init()
                event.start()

    def spin(self, *args):
        """
        Blocking until Ctrl+C is received. Executes given functions in sequence. Functions cannot have arguments.
        :param args: Functions to be executed each iteration.
        :return:
        """
        while not self.__shutdown_requested:
            for f in args:
                f()
            time.sleep(.01)

    def _signal_handler(self, *args):
        print "Caught Ctrl+C, stopping."
        self.__shutdown_requested = True
        print "Executing shutdown functions."
        for event in self.events:
            event[0].stop() if isinstance(event, (tuple, list)) else event.stop()
        for f in self.__on_shutdown: f()
        print "Killing broker"
        con.shutdown_broker(self.broker)
        print "Good-bye"

    def on_shutdown(self, *args):
        """
        Register on shutdown functions. These functions cannot have arguments. You can list as many functions as you
        want. These will be executed in order.
        This can be called multiple times.
        :param args: The function(s) to be called on shutdown.
        """
        args = args if isinstance(args, (list, tuple)) else [args]
        self.__on_shutdown.extend(args)
