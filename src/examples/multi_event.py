from naoqi_interfaces.events.multi_event_abstractclass import MultiEventAbstractclass
import naoqi_interfaces.comms.connection as con
from naoqi_interfaces.control.event_spinner import EventSpinner
import argparse


class MultiEvent(MultiEventAbstractclass):
    def __init__(self):
        super(self.__class__, self).__init__(
            inst=self,
            events=[
                ("PeoplePerception/PeopleDetected", "ALPeoplePerception", self.callback_person),
                ("GazeAnalysis/PeopleLookingAtRobot", "ALGazeAnalysis", self.callback_gaze),
                ("FaceDetected", "ALFaceDetection", self.callback_face)
            ]
        )
        # Using proxies
        print "Detection range:", self.get_proxy("ALPeoplePerception").getMaximumDetectionRange()
        print "Gaze analysis tolerance:", self.ALGazeAnalysis.getTolerance()
        print "Face recognition enabled:", self.ALFaceDetection.isRecognitionEnabled()
        # Proxies can be accessed either via their name as a string using `get_proxy` or directly as a member variable.
        # Variable names for proxies are the same as the string in the event tuple.

    def callback_person(self, *args, **kwargs):
        print "PERSON"
        print args
        print kwargs
        person_id = args[1][1][0][0]
        print person_id
        # Using the memory. Every event class has it's own memory member variable
        print "Distance:", self.memory.getData("PeoplePerception/Person/"+str(person_id)+"/Distance")
        try:
            print "Head angles from gaze analysis:", self.memory.getData(
                "PeoplePerception/Person/" + str(person_id) + "/HeadAngles")
        except RuntimeError:
            print "No gaze information"

    def callback_gaze(self, *args, **kwargs):
        # This callback doesn't do anything. We just need to subscribe to gaze analysis to make sure it is running so we
        # can use it in `callback_person` for memory queries of the head angles.
        pass

    def callback_face(self, *args, **kwargs):
        print "FACE"
        print args
        print kwargs

    def start(self, glob, a, b):
        # Overriding the start function to show how to use custom arguments
        super(MultiEvent, self).start(glob)
        print a, b

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
    s = MultiEvent()

    # Keep alive till Ctrl+C is called
    spinner = EventSpinner(
        globals_=globals(),
        broker=broker,
        events=[(s, ["start", "event"])] # Using custom arguments for MultiEvent.start
    )
    spinner.spin()
