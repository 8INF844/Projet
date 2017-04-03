# -*- encoding: UTF-8 -*-
from naoqi import ALProxy, ALBroker, ALModule

import argparse, time

class StateMachine():
    def __init__(self, instance):
        self.state = None
        self.instance = instance

    def process(self):
        if self.state:
            self.state.process(self.instance)

    def change_state(self, new_state):
        if self.state:
            self.state.exit(self.instance)
        self.state = new_state
        if self.state:
            self.state.enter(self.instance)


class State():
    @staticmethod
    def enter(instance):
        pass
    @staticmethod
    def process(instance):
        pass
    @staticmethod
    def exit(instance):
        pass

class WaitForOwner(State):
    @staticmethod
    def enter(instance):
        # Sit
        instance.motion_proxy.wakeUp()
        instance.posture_proxy.goToPosture('Sit', 0.5)

        # Wait for agent to recognize a face
        instance.face_proxy.subscribe('Test_Face', 500, 0.0)

    @staticmethod
    def process(instance):
        # PERCEPTION
        # See if faces have been detected
        time.sleep(0.5)
        val = instance.memory.getData('FaceDetected')
        if val and isinstance(val, list) and len(val) >= 2:
            instance.faces = val[1]
        else:
            instance.faces = []

        # DECISION
        if instance.faces:
            instance.state_machine.change_state(OfferHelp)

    @staticmethod
    def exit(instance):
        # Unsubscribe to face recognition event
        instance.face_proxy.unsubscribe('Test_Face')

class OfferHelp(State):
    @staticmethod
    def enter(instance):
        # Stand up
        instance.motion_proxy.wakeUp()
        instance.posture_proxy.goToPosture('StandInit', 0.5)


class Agent(ALModule):
    def __init__(self, name, initial_state):
        ALModule.__init__(self, name)
        self.state_machine = StateMachine(self)
        self.initial_state = initial_state
        self.tts = ALProxy('ALTextToSpeech')
        self.face_proxy = ALProxy('ALFaceDetection')
        self.face_proxy.enableTracking(False)
        self.memory = ALProxy('ALMemory')
        self.motion_proxy  = ALProxy('ALMotion')
        self.posture_proxy = ALProxy('ALRobotPosture')
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

    def init(self):
        # Set initial state
        self.state_machine.change_state(self.initial_state)

    def loop(self):
        # Process current state
        self.state_machine.process()

    def end(self):
        # Leave current state
        self.state_machine.change_state(None)

class BearerAssistant(Agent):
    def __init__(self, name):
        Agent.__init__(self, name, WaitForOwner)

    def end(self):
        pass



if __name__ == '__main__':
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument(
        '--ip',
        type=str,
        default='192.168.0.0.1',
        help='Adresse IP du robot.'
    )
    args_parser.add_argument(
        '--port',
        type=int,
        default=9559,
        help='Port du robot.'
    )
    args = args_parser.parse_args()

    # Initialize broker
    broker = ALBroker('broker', '0.0.0.0', 0, args.ip, args.port)

    # Initialize bearer assistant
    global bearer_assistant
    bearer_assistant = BearerAssistant('bearer_assistant')
    bearer_assistant.start()

    # Shut down broker
    broker.shutdown()
