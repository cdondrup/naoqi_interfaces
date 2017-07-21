from naoqi_interfaces.events.multi_event_abstractclass import MultiEventAbstractclass, Event
from naoqi_interfaces.control.event_spinner import EventSpinner
import argparse
import time


class MultiEvent(MultiEventAbstractclass):
    # def __init__(self):
    #     super(MultiEvent, self).__init__(
    #         events=[  # There are three different ways to define an event. proxy_name is the only one that can be None.
    #             ("PeoplePerception/PeopleDetected", "ALPeoplePerception", self.callback_person),  # Tuple
    #             ["GazeAnalysis/PeopleLookingAtRobot", "ALGazeAnalysis", self.callback_gaze],  # List
    #             Event(event_name="FaceDetected", proxy_name="ALGazeAnalysis", callback=self.callback_face)  # Or Event
    #         ]
    #     )

    def callback_person(self, *args, **kwargs):
        print "PERSON"
        print args
        print kwargs
        person_id = args[1][1][0][0]
        print person_id
        # Using the memory. Every event class has it's own memory member variable
        print "Distance:", self.__memory__.getData("PeoplePerception/Person/" + str(person_id) + "/Distance")
        try:
            print "Head angles from gaze analysis:", self.__memory__.getData(
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

    def init(self, glob, a, b):
        # Overriding the init function to show how to use custom arguments. This is optional!
        # The first argument always has to be passed to the super call. This will contain the globals. All arguments
        # after 'glob' can be used to your liking.
        super(MultiEvent, self).init(glob)
        self.a = a
        print a, b
        # Using proxies
        print "Detection range:", self.get_proxy("ALPeoplePerception").getMaximumDetectionRange()
        print "Gaze analysis tolerance:", self.ALGazeAnalysis.getTolerance()
        # print "Face recognition enabled:", self.ALFaceDetection.isRecognitionEnabled()
        # Proxies can be accessed either via their name as a string using `get_proxy` or directly as a member variable.
        # Variable names for proxies are the same as the string in the event tuple.

    def my_control_loop(self):
        print "Loop", self.a
        time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ip", type=str, default="pepper",
                        help="Robot ip address")
    parser.add_argument("-p", "--port", type=int, default=9559,
                        help="Robot port number")
    args = parser.parse_args()

    # Create an instance of the class and init the subscription
    s1 = MultiEvent(
        events=[  # There are three different ways to define an event. proxy_name is the only one that can be None.
            ("PeoplePerception/PeopleDetected", "ALPeoplePerception", "callback_person"),  # Tuple
            ["GazeAnalysis/PeopleLookingAtRobot", "ALGazeAnalysis", "callback_gaze"],  # List
            Event(event_name="FaceDetected", proxy_name="ALGazeAnalysis", callback="callback_face")  # Or Event
        ]
    )
    s2 = MultiEvent(
        events=[  # There are three different ways to define an event. proxy_name is the only one that can be None.
            ("PeoplePerception/PeopleDetected", "ALPeoplePerception", "callback_person"),  # Tuple
            ["GazeAnalysis/PeopleLookingAtRobot", "ALGazeAnalysis", "callback_gaze"],  # List
            Event(event_name="FaceDetected", proxy_name="ALGazeAnalysis", callback="callback_face")  # Or Event
        ]
    )

    # Start the broker, call the 'init' functions of all event classes, and keep alive till Ctrl+C is called
    spinner = EventSpinner(
        globals_=globals(),
        ip=args.ip,
        port=args.port,
        events=[
            (s1, ["instance 1", "some string"]),
            (s2, ["instance 2", 5])
        ]  # Using custom arguments for init function. If no arguments are to be given just use: events=[s1,s2]
    )
    # The spinner can call arbitrary functions without arguments while running.
    spinner.spin(s1.my_control_loop, s2.my_control_loop)
