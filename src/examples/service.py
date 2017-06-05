from naoqi_interfaces.services.service_proxy import ServiceProxy


class AnimatedSay(object):
    def __init__(self):
        self.speech = ServiceProxy(proxy_name="ALAnimatedSpeech")
        self.configuration = {"bodyLanguageMode": "contextual"}

    def say(self, text):
        self.speech.say(text, self.configuration)
