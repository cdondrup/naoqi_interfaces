import signal
import time


class Spinner(object):
    def __init__(self):
        self.__shutdown_requested = False
        signal.signal(signal.SIGINT, self._signal_handler)

    def spin(self, *args):
        while not self.__shutdown_requested:
            for f in args:
                f()
            time.sleep(.1)

    def _signal_handler(self, *args):
        print('Caught Ctrl+C, stopping.')
        self.__shutdown_requested = True
        print('Good-bye')
