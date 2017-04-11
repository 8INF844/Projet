from core.states import State
import time


class WaitForOwner(State):
    @staticmethod
    def enter(instance):
        print('[WaitForOwner]enter')
        # Sit
        instance.motion.wakeUp()
        instance.posture.goToPosture('Sit', 0.5)

        # Wait for agent to recognize a face
        instance.face_detection.subscribe('Test_Face', 500, 0.0)

    @staticmethod
    def process(instance):
        print('[WaitForOwner]process')
        # See if faces have been detected
        time.sleep(0.5)
        data = instance.memory.getData('FaceDetected')
        if data and isinstance(data, list) and len(data) >= 2:
            instance.faces = data[1]
        else:
            instance.faces = []

        if instance.faces:
            instance.state_machine.change_state(OfferHelp)

    @staticmethod
    def exit(instance):
        print('[WaitForOwner]exit')
        # Unsubscribe to face recognition event
        instance.face_detection.unsubscribe('Test_Face')


class OfferHelp(State):
    @staticmethod
    def enter(instance):
        print('[OfferHelp]enter')
        # Stand up
        instance.motion.wakeUp()
        instance.posture.goToPosture('StandInit', 0.5)
        # Offer help
        instance.text_to_speech.say('Puis-je prendre un objet ?')
        # Listen to response
        vocabulary = ['oui', 'non']
        try:
            instance.memory.unsubscribeToEvent('WordRecognized', 'AgentNao')
        except:
            pass
        instance.speech_recognition.pause(True)
        instance.speech_recognition.setVocabulary(vocabulary, False)
        instance.speech_recognition.pause(False)
        instance.memory.subscribeToEvent('WordRecognized', instance.name,
                                         'on_word_recognized')

    @staticmethod
    def process(instance):
        print('[OfferHelp]process')
        for word in instance.words_recognized:
            print(word)
            if word['value'] == 'oui':
                instance.state_machine.change_state(TakeObject)
            elif word['value'] == 'non':
                instance.state_machine.change_state(WaitForOwner)
        instance.words_recognized = []

    @staticmethod
    def exit(instance):
        print('[OfferHelp]exit')
        # Stop listening to response
        instance.memory.unsubscribeToEvent('WordRecognized', instance.name)


class TakeObject(State):
    @staticmethod
    def enter(instance):
        print('[TakeObject]enter')
        # Move to person

        # Open hand
        instance.motion_proxy.wakeUp()
        instance.motion_proxy.stiffnessInterpolation('Body', 1.0, 1.0)
        effector = 'RArm'
        space = motion.FRAME_ROBOT
        axis_mask = almath.AXIS_MASK_VEL
        is_absolute = False
        current_pos = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        target_pos = [0.1, 0.0, 0.12, 0.0, 0.0, 0.0]
        path = [curret_pos, target_pos]
        times = [2.0, 4.0]
        instance.motion_proxy.positionInterpolation(effector, space, path,
                axis_mask, times, is_absolute)
        instance.motion_proxy.openHand(effector)

        # Wait for object given
        instance.memory.subscribeToEvent('TouchChanged', instance.name,
                'on_touched')

    @staticmethod
    def process(instance):
        # Object in ?
        if 'RArm' in instance.touched_sensors:
            instance.motion_proxy.closeHand('RHand')
            instance.touched_sensors = []
            instance.state_machine.change_state(WaitForSomeoneElse)

        # Wait for too long ?
        # > [WaitForOwner]
        pass

    @staticmethod
    def exit(instance):
        # Don't wait for object anymore
        instance.memory.unsubscribeToEvent('TouchChanged', instance.name)
        pass

class WaitForSomeoneElse(State):
    @staticmethod
    def enter(instance):
        # Turn 180 degree
        pass
        # Wait for new person

    @staticmethod
    def process(instance):
        # Person found ?
        # > [BringObject]
        # Wait for too long
        # > Drop Object
        # > [WaitForOwner]
        pass

    @staticmethod
    def process(instance):
        pass

class BringObject(State):
    @staticmethod
    def enter(instance):
        # Move to person

        # Wait for person ready

        pass

    @staticmethod
    def process(instance):
        # Person ready ?
        # > Open hand
        # > [WaitForOwner]
        # Wait for too long ?
        # > Drop object
        # > [WaitForOwner]
        pass

    @staticmethod
    def exit(instance):
        pass
