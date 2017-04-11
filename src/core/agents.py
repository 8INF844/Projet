from naoqi import ALProxy, ALBroker
from states import StateMachine


class DefaultAgent():
    """
    Base structure of an agent, loading all standard Nao modules.
    """
    def __init__(self, name, ip, port=9559):
        self.name = name
        # Initialize broker
        self.broker = ALBroker('broker', '0.0.0.0', 0, ip, port)
        # Initialize standard proxies
        self.text_to_speech = ALProxy('ALTextToSpeech')
        self.face_detection = ALProxy('ALFaceDetection')
        self.face_detection.enableTracking(False)
        self.memory = ALProxy('ALMemory')
        self.motion = ALProxy('ALMotion')
        self.posture = ALProxy('ALRobotPosture')
        self.speech_recognition = ALProxy('ALSpeechRecognition')
        self.speech_recognition.setLanguage('French')

    def start(self):
        self.init()
        try:
            while True:
                self.loop()
        except KeyboardInterrupt:
            pass
        self.end()

    def init():
        pass

    def loop():
        pass

    def end():
        pass


class StatesAgent(DefaultAgent):
    """
    Special agent based on a state machine.
    """
    def __init__(self, *args, **kwargs):
        DefaultAgent.__init__(self, *args, **kwargs)
        self.state_machine = StateMachine(self)

    def init(self):
        pass

    def loop(self):
        self.state_machine.process()

    def end(self):
        self.state_machine.change_state(None)
