from core.states import State
import time

class WaitForOwner(State):
    @staticmethod
    def enter(instance):
        # Sit
        instance.motion.wakeUp()
        instance.posture.goToPosture('Sit', 0.5)

        # Wait for agent to recognize a face
        instance.face_detection.subscribe('Test_Face', 500, 0.0)

    @staticmethod
    def process(instance):
        # PERCEPTION
        # See if faces have been detected
        time.sleep(0.5)
        data = instance.memory.getData('FaceDetected')
        if data and isinstance(data, list) and len(data) >= 2:
            instances.faces = data[1]
        else:
            instances.faces = []

        # DECISION
        if instance.faces:
            instance.state_machine.chenge_state(OfferHelp)

    @staticmethod
    def exit(instance):
        # Unsubscribe to face recognition event
        instance.face_detection.unsubscribe('Test_Face')

class OfferHelp(State):
    @staticmethod
    def enter(instance):
        # Stand up
        instance.motion.wakeUp()
        instance.posture.goToPosture('StandInit', 0.5)

