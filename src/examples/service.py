from naoqi_interfaces.services.service_proxy import ServiceProxy
import naoqi_interfaces.comms.connection as con
import argparse


class AnimatedSay(object):
    def __init__(self):
        self.speech = ServiceProxy(proxy_name="ALAnimatedSpeech")
        self.configuration = {"bodyLanguageMode": "contextual"}

    def say(self, text):
        self.speech.say(text, self.configuration)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ip", type=str, default="pepper",
                        help="Robot ip address")
    parser.add_argument("-p", "--port", type=int, default=9559,
                        help="Robot port number")
    args = parser.parse_args()

    # Create a broker to connect to the robot
    broker = con.create_broker(args.ip, args.port)

    # Create an instance of the class and init the subscription
    s = AnimatedSay()
    s.say("Hello World!")

    # No spinner as this does not use events but simply calls the service once.

    con.shutdown_broker(broker)
