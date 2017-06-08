from naoqi_interfaces.events.event_abstractclass import EventAbstractclass
import naoqi_interfaces.comms.connection as con
from naoqi_interfaces.control.event_spinner import EventSpinner
import argparse


class SingleEvent(EventAbstractclass):
    EVENT_NAME = "PeoplePerception/PeopleDetected"
    PROXY_NAME = "ALPeoplePerception"

    def __init__(self):
        super(self.__class__, self).__init__(inst=self, event=self.EVENT_NAME, proxy_name=self.PROXY_NAME)

        # Using proxies. This can be done with get_proxy function or using them as member variables directly. Variable
        # names are defined by the proxy_name string.
        print "Face detection enabled:", self.get_proxy(self.PROXY_NAME).isFaceDetectionEnabled()
        # If the string is omitted, the proxy created using the super call is returned.
        print "Detection range:", self.get_proxy().getMaximumDetectionRange()
        # All proxies can be used as a member variables directly
        print "Movement detection:", self.ALPeoplePerception.isMovementDetectionEnabled()

    # Overriding the abstract callback from EventAbstractclass
    def callback(self, *args, **kwargs):
        # Print the results
        print args
        print kwargs

        person_id = args[1][1][0][0]
        print "Person ID:", person_id
        # Using the memory. Every event class has it's own memory member variable
        print "Distance:", self.memory.getData("PeoplePerception/Person/" + str(person_id) + "/Distance")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ip", type=str, default="pepper",
                        help="Robot ip address")
    parser.add_argument("-p", "--port", type=int, default=9559,
                        help="Robot port number")
    args = parser.parse_args()

    # Create a broker to connect to the robot
    broker = con.create_broker(args.ip, args.port)

    # Create an instance of the class and start the subscription
    s = SingleEvent()

    # Start subscribing and keep alive till Ctrl+C is called
    spinner = EventSpinner(
        globals_=globals(),
        broker=broker,
        events=[s]
    )
    spinner.spin()
