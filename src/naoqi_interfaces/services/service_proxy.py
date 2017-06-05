from naoqi import ALProxy


class ServiceProxy(object):
    def __init__(self, proxy_name):
        """
        Creates a proxy for simple service calls. Proxies can be called in different ways:
        
        service = ServiceProxy("ALAnimatedSpeech")
        service.ALAnimatedSpeech.say("test")
        service.proxy.say("test")
        service.say("test")
        
        All do the same.
        
        :param proxy_name: The name of the proxy to create, e.g. ALAnimatedSpeech
        """
        if not isinstance(proxy_name, str):
            raise TypeError("Proxy names have to be string objects.")
        self.proxy_name = proxy_name
        setattr(self, proxy_name, ALProxy(proxy_name))

    def __getattr__(self, item):
        return getattr(self.proxy, item)

    @property
    def proxy(self):
        return getattr(self, self.proxy_name)
