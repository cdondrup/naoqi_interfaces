import signal
import time


class Spinner(object):
    """
    A simple spinner that helps keeping the programme alive while reacting to events.
    """
    def __init__(self):
        self.__shutdown_requested = False
        self.__on_shutdown = []
        signal.signal(signal.SIGINT, self._signal_handler)

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
        for f in self.__on_shutdown: f()
        print 'Good-bye'

    def register_on_shutdown_function(self, *args):
        """
        Register functions to be executed on shutdown. Only functions without arguments can be used.
        Use lambda function to create argument less calls for functions that do have arguments. E.g.

        shutdown_broker(broker)

        turns into

        lambda: shutdown_broker(broker)

        :param args: The function(s) to be called.
        """
        self.__on_shutdown.extend(args)
