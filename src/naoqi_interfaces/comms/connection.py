from naoqi import ALBroker
import time
import uuid


def create_broker(ip, port, target_ip="0.0.0.0", target_port=0):
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
        return create_broker(ip, port)


def shutdown_broker(broker):
    broker.shutdown()
