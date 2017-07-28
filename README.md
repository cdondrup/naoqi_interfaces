# naoqi_interfaces

This package provides a few conveneince interfaces for naoqi. Have a look at the examples.

## Installation

Checkout the repository and add the path to the src folder to your PYTHONPATH:

```
export PYTHONPATH=$PYTHONPATH:/path/to/naoqi_interfaces/src
```

## Usage

This packages offers some conveneince functions to deal with connecting to naqi on the robot or choreograhp, manageing the connection, subscribing to events, and creating proxies. In the following I will give an overview of the most important classes and functions.

### Single Events

In order to subscribe to certain events in naoqi you normally have to deal with a bunch of global variables and neboulous strings. To facilitate the usage, this package provides two simple classes that can be extended. The `EventAbstractclass` can be used if you onlt want to subscribe to to a single event. For multiple events in the same class, see below.

In order to subscribe to a single event, you just have to create a class that inherits from `EvenAbstractclass` and overrides its `callback` method:

```python
from naoqi_interfaces.events.event_abstractclass import EventAbstractclass
...


class SingleEvent(EventAbstractclass):
    # Overriding the abstract callback from EventAbstractclass
    def callback(self, *args, **kwargs):
        # Print the results
        print args
        print kwargs
```

The class can then be instatiated using the constructor of the super class:

```python
s = SingleEvent(
	event="/Event/name",
	proxy_name="ALMyProxy"
)
```

The `proxy_name` can also be omitted if your class does not rely on a specific proxy but for example a custom event you created elsewhere. The `callback` function will be called whenever data is published on the specified event. An example application would be to get the distance of all the people in front of the robot:

```python
from naoqi_interfaces.events.event_abstractclass import EventAbstractclass
...


class SingleEvent(EventAbstractclass):
    # Overriding the abstract callback from EventAbstractclass
    def callback(self, *args, **kwargs):
        # Print the results
        print args
        print kwargs

        for person in args[1][1]: # These indexes are different depending on the data published by the event.
            person_id = person[0] # What data is published can be found in the naoqi documentation.
            print "Person ID:", person_id
            # Using the memory. Every event class has it's own memory member variable
            print "Distance:", self.__memory__.getData("PeoplePerception/Person/" + str(person_id) + "/Distance")


if __name__ == "__main__":
	...

	# Create an instance of the class
    s = SingleEvent(
        event="PeoplePerception/PeopleDetected",
        proxy_name="ALPeoplePerception"
    )

    ...
```

Eventhough the distance is already part of the data published by the event, this demonstrates how to use ALMemory when using the event class. Every class that inherits from `EventAbstractclass` or `MultiEventAbstractclass` automatically has access to the memory via the `__memory__` member variable. This supports all the functionality of an ALMemory proxy like `getData`. There is no need to create your own instance of that proxy.

Since the people perception relies on the `ALPeoplePerception` module to run, we specify this as the `proxy_name` which creates an instance of it. For how to use proxies in the event classes, see below.

### Multiple Events

Just subscribing to a single event might not be enough and you want to have data from different events in the same class to be able to make an informed decision based on multi modal input. In order to be able to subscribe to multiple events in the same class, all you have to do is create a class that inherits from `MultiEventAbstractclass`. Let's assume you would like to know the distance of all the people in front of the robot, their head angles, and print some information about face characteristics:

```python
from naoqi_interfaces.events.multi_event_abstractclass import MultiEventAbstractclass, Event
...


class MultiEvent(MultiEventAbstractclass):
    def callback_person(self, *args, **kwargs):
        print "PERSON"
        print args
        print kwargs
        for person in args[1][1]: # These indexes are different depending on the data published by the event.
            person_id = person[0] # What data is published can be found in the naoqi documentation.
            print "Person ID:", person_id
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
```

As you can see, you simpky define three callbacks and give them arbitrary names. The `callback_gaze` is a spcial case. You can see it does not do anything but in order for the data about the head angles to be available via the memory, your component has to subscribe to an event published by `ALGazeAnalysis`. The try-except block in the `callback_person` is only used bacuse the robot might not have head angles for every visble person all the time as this depends on wether the face can be seen or not. The last callback `callback_face` simnply prints some data.

There are two possible ways of creating an instance of this class. The easiest is to use a syntax analogus to the eone for the single event:

```python
if __name__ == "__main__":
	...

	s = MultiEvent(
	    events=[
	        ("PeoplePerception/PeopleDetected", "ALPeoplePerception", "callback_person"),
	        ["GazeAnalysis/PeopleLookingAtRobot", "ALGazeAnalysis", "callback_gaze"],
	        Event(event_name="FaceDetected", proxy_name="ALGazeAnalysis", callback="callback_face")
	    ]
	)

	...
```

As you can see there are a few differences between the single event construction and the multi event construction. Since we don't know how many events you want to subscribe to at the same time, the only argument that is required is a list of events which can have three different possible entries. The most verbose way of creating one of these events is to use the `Event` class. This provides a constructor with name fields and makes it therefore explicit which string is what:

```python
Event(
	event_name="FaceDetected",
	proxy_name="ALGazeAnalysis", 
	callback="callback_face"
)
```

When used with the keyword, the order does not matter and the `proxy_name` can be omitted like in the single event case if no proxy is required for this event. The other options of defining the event name, proxy name, and callback are either a tuple or a list where the order of the elements matter. First: event name, second: proxy name, third callback name. The proxy name can be set to `None` if not required. All the three can be mixed as well. The recommended way of doing this is to the provided `Event` class.

As you can see, the callback is defined via a string which has to be the same as the function name. I flike me you are not fond of having strings that need to be the same as function or class names, etc. then there is a different way of constructing the `MultiEvent` class:

```python
from naoqi_interfaces.events.multi_event_abstractclass import MultiEventAbstractclass, Event
...


class MultiEvent(MultiEventAbstractclass):
    def __init__(self):
        super(MultiEvent, self).__init__(
            events=[
                ("PeoplePerception/PeopleDetected", "ALPeoplePerception", self.callback_person),
                ["GazeAnalysis/PeopleLookingAtRobot", "ALGazeAnalysis", self.callback_gaze],
                Event(event_name="FaceDetected", proxy_name="ALGazeAnalysis", callback=self.callback_face)
            ]
        )

...

if __name__ == "__main__":
	...

	s = MultiEvent()

	...
```

As you can see, by overriding the `__init__` function and calling the super `__init__` function you can also sepcify the callback directly as a function of this class. Both ways are equivalent and just depend on your prefences.

### Event Manager

In order to connect to the robot, subscribe your callbacks to the events, and keep the program alive, this packages use the `EventManager` which does a lot of the black magic of naoqi for you. After you contrsucted your event(s), you have to create and instance of the `EventManager`:

```python
...
from naoqi_interfaces.control.event_manager import EventManager

...

if __name__ == "__main__":
	...

	s = MultiEvent(
        events=[  # There are three different ways to define an event. proxy_name is the only one that can be None.
            ("PeoplePerception/PeopleDetected", "ALPeoplePerception", "callback_person"),  # Tuple
            ["GazeAnalysis/PeopleLookingAtRobot", "ALGazeAnalysis", "callback_gaze"],  # List
            Event(event_name="FaceDetected", proxy_name="ALGazeAnalysis", callback="callback_face")  # Or Event
        ]
    )

    ...

    man = EventManager(
        globals_=globals(),
        ip="127.0.0.1",
        port="12345",
        events=[s]
    )
	man.spin() # Blocks until Ctrl+C is caught

    ...
```

In order to do all the black magic with the global variables naoqi requires, the `EventManager` has to be instanciated in the python file that is executed. Imagine you have a few different classes in separate files and a main file which is the one the is executed. The `EventManager` has to be in this main file and the `globals_` argument of the constructor always needs access to the dictionary holding the global variables of the executed file. This is simply achieved via `globals_=globals()` in the constructor. The `ip` is the IP of the robot or choregraph you want to connect to and the `port` is the corresponding port. The last argument holds a list of all the classes that inherit from `EventAbstractclass` or `MultiEventAbstractclass`.

The constructor of the `EventManager` starts all the subscriptions for all your events. This means that once the instance has been constructed, data will be received.

The call to the `spin()` function simply keeps the program alive until `Ctrl+C` is caught after which everything will be shut down.

### Service Proxies

If you don't want to use an event but just make  few calls to functions of proxies, you can use the `ServiceProxy` class. An easy exampkle would be to make pepper say something:

```python
from naoqi_interfaces.services.service_proxy import ServiceProxy
import naoqi_interfaces.comms.connection as con


class AnimatedSay(object):
    def __init__(self):
        self.speech = ServiceProxy(proxy_name="ALAnimatedSpeech")
        self.configuration = {"bodyLanguageMode": "contextual"}

    def say(self, text):
        self.speech.say(text, self.configuration)


if __name__ == "__main__":
    # Create a broker to connect to the robot
    broker = con.create_broker("127.0.0.1", "12345")

    # Create an instance of the class and init the subscription
    s = AnimatedSay()
    s.say("Hello World!")

    con.shutdown_broker(broker)
```

As you can see we constructed a simple class that inherits from `object` and contains a `ServiceProxy` of `ALAnimatedSpeech` which provides a `say` function. Since this no event, we don't need an `EventManager` and therefore we create a connection to the robot ourselves using the `create_broker` function and shut it down after wards with the `shutdown_broker` function.


## Advanced Usage

All examples above are very simple but do not allow for much added functionality except for doing things in a callback.

### Using proxies in events

Let's assume you would like use the proxy you specified when you created your single event or multi event class. Taking the single event example where we used the `ALPeoplePerception` proxy there are three different ways of using it:

```python
print "Face detection enabled:", self.get_proxy(self.__proxy_name__).isFaceDetectionEnabled()
print "Detection range:", self.get_proxy().getMaximumDetectionRange()
print "Movement detection:", self.ALPeoplePerception.isMovementDetectionEnabled()
```

All these are equivalent and just depend on your choice. The `get_proxy` function provides the proxy that is specified via a string of it's name or the proxy that was used during creation of the instance if the string is omitted. The `__proxy_name__` variable is provided by the `EventAbstractclass`. Alternatively, the proxies can be acces directly via their member varaible. Whenever a proxy is created, it is saved in a variable of the same name. So the `ALPeoplePerception` proxy is accessible via `self.ALPeoplePerception`.

### Creating proxies in events

If you need additional proxies apart from the ones that were created for your event subscriptions, you can simply used the `create_proxy` function:

```python
self.create_proxy("ALTracker")
```

inside your class. Afterwards, the proxy is accessible as described above.


### Initialising Events

Since a connection to the robot might not have been created when you instanciate your event, you cannot use any calls to proxies or create any proxies in the constructor of your class that inherits from `EventAbstractclass` or `MultiEventAbstractclass`. To be able to make calls to proxies before the callbacks are subscribed to the events, you can override the `init` function:

```python
...


class SingleEvent(EventAbstractclass):
    def init(self, *args):
        # Overriding the init function to show how to use proxies. This is optional!
        # Using proxies. This can be done with get_proxy function or using them as member variables directly. Variable
        # names are defined by the proxy_name string.
        print "Face detection enabled:", self.get_proxy(self.__proxy_name__).isFaceDetectionEnabled()
        # If the string is omitted, the proxy created using the super call is returned.
        print "Detection range:", self.get_proxy().getMaximumDetectionRange()
        # All proxies can be used as a member variable directly
        print "Movement detection:", self.ALPeoplePerception.isMovementDetectionEnabled()

    ...

if __name__ == "__main__":
	...

	# Create an instance of the class
    s = SingleEvent(
        event="PeoplePerception/PeopleDetected",
        proxy_name="ALPeoplePerception"
    )

	...

    man = EventManager(
        globals_=globals(),
        ip="127.0.0.1",
        port="12345",
        events=[s]
    )
	man.spin() # Blocks until Ctrl+C is caught

```

This can be used equivalently for classes inheriting from `MultiEventAbstractclass`. This function is called by the `EventManager` before it subscribes your callbacks to the events but after a connection to the robot has been created.

If you require to pass arguments to the init function, you simply do so in the constructor of the `EventManager`:

```python
...


class SingleEvent(EventAbstractclass):
    def init(self, *args):
    	print args[0], args[1]

        # Overriding the init function to show how to use proxies. This is optional!
        # Using proxies. This can be done with get_proxy function or using them as member variables directly. Variable
        # names are defined by the proxy_name string.
        print "Face detection enabled:", self.get_proxy(self.__proxy_name__).isFaceDetectionEnabled()
        # If the string is omitted, the proxy created using the super call is returned.
        print "Detection range:", self.get_proxy().getMaximumDetectionRange()
        # All proxies can be used as a member variable directly
        print "Movement detection:", self.ALPeoplePerception.isMovementDetectionEnabled()

    ...

if __name__ == "__main__":
	...

	# Create an instance of the class
    s = SingleEvent(
        event="PeoplePerception/PeopleDetected",
        proxy_name="ALPeoplePerception"
    )

	...

    man = EventManager(
        globals_=globals(),
        ip="127.0.0.1",
        port="12345",
        events=[(s, ["my custom argument", 5])]
    )
	man.spin() # Blocks until Ctrl+C is caught

```

The list of event classes `events` can hold either instances of classes that inherit from `EventAbstractclass`, `MultiEventAbstractclass`, or tuples. If it is a tuple, the first element has to be the class instance and the second element has to be a list of custom arguments to be given to the `init` function. You can mix tuples and class instances freely within the list given to `events`.

### Control Loop

Imagine you want to build your own little state machine inside your `MultiEvent` class that relies on multimodal input from several events. This is easily done using the `spin` function of the `EventManager`. Taking above example of the `MultiEvent` class:

```python
from naoqi_interfaces.events.multi_event_abstractclass import MultiEventAbstractclass, Event
from naoqi_interfaces.control.event_manager import EventManager
...


class MultiEvent(MultiEventAbstractclass):
    def callback_person(self, *args, **kwargs):
        self.persons = args

    def callback_gaze(self, *args, **kwargs):
        # This callback doesn't do anything. We just need to subscribe to gaze analysis to make sure it is running so we
        # can use it in `callback_person` for memory queries of the head angles.
        pass

    def callback_face(self, *args, **kwargs):
        self.faces = args

    def my_control_loop(self):
    	for person in self.persons[1][1]: # These indexes are different depending on the data published by the event.
            person_id = person[0] # What data is published can be found in the naoqi documentation.
            print "Person ID:", person_id
	        # Using the memory. Every event class has it's own memory member variable
	        print "Distance:", self.__memory__.getData("PeoplePerception/Person/" + str(person_id) + "/Distance")
	        try:
	            print "Head angles from gaze analysis:", self.__memory__.getData(
	                "PeoplePerception/Person/" + str(person_id) + "/HeadAngles")
	        except RuntimeError:
	            print "No gaze information"
	    print self.faces

if __name__ == "__main__":
	...

	s = MultiEvent(
        events=[  # There are three different ways to define an event. proxy_name is the only one that can be None.
            ("PeoplePerception/PeopleDetected", "ALPeoplePerception", "callback_person"),  # Tuple
            ["GazeAnalysis/PeopleLookingAtRobot", "ALGazeAnalysis", "callback_gaze"],  # List
            Event(event_name="FaceDetected", proxy_name="ALGazeAnalysis", callback="callback_face")  # Or Event
        ]
    )

    ...

    man = EventManager(
        globals_=globals(),
        ip="127.0.0.1",
        port="12345",
        events=[s]
    )
	man.spin(s.my_control_loop) # Blocks until Ctrl+C is caught
```

As you can see above, we moved all the printing into the `my_control_loop` function. Of course you will want to do some calculations and decision making based on this but we are just printing things for now. The last line of the file `man.spin(s.my_control_loop)` shows that the `spin` function takes functions an argument. Internally, the `spin` function is just a loop with a .01 seonds wait. During that loop it will execute allo the functions it got as an argument in sequence. So if there are multiple functions: `man.spin(s.my_control_loop, ...)` the `s.my_control_loop` would always be first to be executed. These function cannot have arguments. Of course python offers a simple trick to circumvent this using lanbda functions:

```python
man.spin(lambda: s.my_control_loop("some string"))
```

Which now passes `some string` to the function it is called while still not requireing any arguments.

### Shutdoen functions

If you want to execute a certain function at shutdown, you can either call it after the `spin` function which blocking or you regiter it with the `EventManager` which will then call this function when it is shutting down but before the broker is disconnected. Hence, if you require to call a proxy at shutdown, you need to register this call as a shutdown function:

```python
man = EventManager(
    globals_=globals(),
    ip="127.0.0.1",
    port="12345",
    events=[...]
)
p = ServiceProxy("ALAnimatedSay")
man.on_shutdown(lambda: p.say("Good bye"))
man.spin()
```

Again, like above, the function registered cannot have any arguments but as above we circumvent this by using the `lambda` trick. You can pass any number of functions to the `on_shutdown` method or call it multiple times. The shutdown functions are executed in the sequence they were added.

Note, the `ServiceProxy` has to be created after the `EventManager` to make sure that there is a connection to the robot.
