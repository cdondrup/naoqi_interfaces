from naoqi import ALBroker
import time
import uuid


def create_broker(ip, port, target_ip="0.0.0.0", target_port=0):
    """
    creates a broker that takes care of the connection between the modules. Call this function in the main file.

    :param ip: The IP to connect to. Usually the IP of the robot.
    :param port: The port to connect to, usually the port of the robot
    :param target_ip: IP to listen to
    :param target_port: Port to use
    :return: The broker instance. Keep this alive in your main file.
    """
    name = str(uuid.uuid4())
    try:
        broker = ALBroker(name,
                          target_ip,  # listen to anyone
                          target_port,  # find a free port and use it
                          ip,  # parent broker IP
                          port)
        print("Connected to %s:%s" % (ip, str(port)))
        return broker
    except RuntimeError:
        print("Cannot connect to %s:%s. Retrying in 1 second." % (ip, str(port)))
        time.sleep(1)
        return create_broker(ip, port, target_ip=target_ip, target_port=target_port)


def shutdown_broker(broker):
    """
    Terminates connection and shuts down the broker. Call in destructor or before ending your script
    :param broker: The broker instance create with create_broker
    """
    broker.shutdown()
