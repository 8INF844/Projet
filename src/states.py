from core.states import State
import time
import motion
import almath
import math


class WaitForOwner(State):
    @staticmethod
    def enter(instance):
        print('[WaitForOwner]enter')
        # Sit
        instance.autonomous_life.setState('solitary')
        instance.motion.wakeUp()
        instance.posture.goToPosture('Sit', 0.5)

        # Wait for agent to recognize a face
        instance.face_detection.subscribe('Test_Face', 500, 0.0)

    @staticmethod
    def process(instance):
        print('[WaitForOwner]process')
        # See if faces have been detected
        data = instance.memory.getData('FaceDetected')
        if data and isinstance(data, list) and len(data) >= 2:
            instance.faces = data[1]
        else:
            instance.faces = []

        if instance.faces:
            instance.state_machine.change_state(OfferHelp)
        time.sleep(0.5)

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
        vocabulary = ['oui', 'non', 'yes', 'no']
        try:
            instance.memory.unsubscribeToEvent('WordRecognized', 'baeh')
        except:
            pass
        instance.speech_recognition.pause(True)
        instance.speech_recognition.setVocabulary(vocabulary, False)
        instance.speech_recognition.pause(False)
        instance.memory.subscribeToEvent('WordRecognized', 'baeh',
                                         'on_word_recognized')

    @staticmethod
    def process(instance):
        print('[OfferHelp]process')
        for word in instance.words_recognized:
            print(word)
            if word in ['yes', 'oui']:
                instance.state_machine.change_state(GoToPersonWithObject)
            elif word in ['non', 'no']:
                instance.state_machine.change_state(WaitForOwner)
        instance.words_recognized = []
        time.sleep(1)

    @staticmethod
    def exit(instance):
        print('[OfferHelp]exit')
        # Stop listening to response
        instance.memory.unsubscribeToEvent('WordRecognized', 'baeh')


class GoToPersonWithObject(State):
    @staticmethod
    def enter(instance):
        print('[GoToPersonWithObject]enter')
        instance.autonomous_life.setState('solitary')
        instance.face_detection.subscribe('Test_Face', 500, 0.5)

    @staticmethod
    def process(instance):
        print('[GoToPersonWithObject]process')

        data = instance.memory.getData('FaceDetected')
        if data and isinstance(data, list) and len(data) >= 2:
            instance.faces = data[1]
        else:
            instance.faces = None

        threshold = 0.1
        if instance.faces:
            first_face = instance.faces[0][0]
            print(first_face)
            if first_face[3] < threshold:
                print(first_face)
                d = math.sqrt(1.25 * math.pow(threshold / first_face[3], 2) - 1) - 0.5
                print(d)
                instance.motion.moveTo(d, 0, first_face[1])  # parachute
            instance.state_machine.change_state(TakeObject)
        time.sleep(0.5)

    @staticmethod
    def exit(instance):
        print('[GoToPersonWithObject]exit')
        instance.face_detection.unsubscribe('Test_Face')


class TakeObject(State):
    @staticmethod
    def enter(instance):
        print('[TakeObject]enter')
        instance.autonomous_life.setState('disabled')
        instance.motion.wakeUp()

        # Open hand
        instance.motion.wakeUp()
        instance.motion.stiffnessInterpolation('Body', 1.0, 1.0)
        effector = 'RArm'
        space = motion.FRAME_ROBOT
        axis_mask = almath.AXIS_MASK_VEL
        is_absolute = False
        current_pos = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        target_pos = [0.1, 0.0, 0.12, 0.0, 0.0, 0.0]
        path = [current_pos, target_pos]
        times = [2.0, 4.0]
        instance.motion.positionInterpolation(effector, space, path,
                                              axis_mask, times,
                                              is_absolute)
        instance.motion.openHand('RHand')

        # Wait for object given
        instance.memory.subscribeToEvent('TouchChanged', 'baeh', 'on_touched')

    @staticmethod
    def process(instance):
        print('[TakeObject]process')
        # Object in ?
        if 'RArm' in instance.touched_sensors:
            instance.motion.closeHand('RHand')
            instance.touched_sensors = []
            instance.state_machine.change_state(WaitForSomeoneElse)

        # Wait for too long ?
        # > [WaitForOwner]
        time.sleep(1)

    @staticmethod
    def exit(instance):
        print('[TakeObject]exit')
        # Don't wait for object anymore
        instance.memory.unsubscribeToEvent('TouchChanged', 'baeh')


class WaitForSomeoneElse(State):
    @staticmethod
    def enter(instance):
        print('[WaitForSomeoneElse]exit')
        # Turn 180 degree
        instance.motion.moveTo(0, 0, math.pi)

        # Wait for new person
        instance.face_detection.subscribe('Test_Face', 500, 0.0)

    @staticmethod
    def process(instance):
        print('[WaitForSomeoneElse]process')
        # See if faces have been detected
        data = instance.memory.getData('FaceDetected')
        if data and isinstance(data, list) and len(data) >= 2:
            instance.faces = data[1]
        else:
            instance.faces = []
        if instance.faces:
            instance.state_machine.change_state(MoveToOtherPerson)
        time.sleep(1)

        # Wait for too long
        # > Drop Object
        # > [WaitForOwner]

    @staticmethod
    def exit(instance):
        print('[WaitForSomeoneElse]exit')
        # Unsubscribe to face recognition event
        instance.face_detection.unsubscribe('Test_Face')


class MoveToOtherPerson(State):
    @staticmethod
    def enter(instance):
        print('[GoToPersonWithObject]enter')
        instance.autonomous_life.setState('solitary')
        instance.face_detection.subscribe('Test_Face', 500, 0.5)

    @staticmethod
    def process(instance):
        print('[GoToPersonWithObject]process')

        data = instance.memory.getData('FaceDetected')
        if data and isinstance(data, list) and len(data) >= 2:
            instance.faces = data[1]
        else:
            instance.faces = None

        threshold = 0.1
        if instance.faces:
            first_face = instance.faces[0][0]
            print(first_face)
            if first_face[3] < threshold:
                print(first_face)
                d = math.sqrt(1.25 * math.pow(threshold / first_face[3], 2) - 1) - 0.5
                print(d)
                instance.motion.moveTo(d, 0, first_face[1])  # parachute
            instance.state_machine.change_state(ReleaseObject)
        time.sleep(0.5)

    @staticmethod
    def exit(instance):
        print('[GoToPersonWithObject]exit')
        instance.face_detection.unsubscribe('Test_Face')


class ReleaseObject(State):
    @staticmethod
    def enter(instance):
        print('[BringObject]enter')
        # Move to person

        # Wait for person ready
        instance.memory.subscribeToEvent('TouchChanged', 'baeh', 'on_touched')

    @staticmethod
    def process(instance):
        print('[BringObject]process')
        # Person ready ?
        if 'RArm' in instance.touched_sensors:
            instance.motion.openHand('RHand')
            instance.touched_sensors = []
            instance.state_machine.change_state(TellJoke)

        # > Open hand
        # > [WaitForOwner]
        # Wait for too long ?
        # > Drop object
        # > [WaitForOwner]
        time.sleep(1)

    @staticmethod
    def exit(instance):
        print('[BringObject]exit')
        # Don't wait for object anymore
        instance.memory.unsubscribeToEvent('TouchChanged', 'baeh')

class TellJoke(State):
    @staticmethod
    def process(instance):
        time.sleep(60)
        instance.text_to_speech.say('Oh ! Désolé de te couper mais je viens de me souvenir d\'une blague bien drole.')
        time.sleep(5)
        instance.text_to_speech.say('Un jour Dieu dit à Casto de ramer. Depuis Castorama...')

        instance.state_machine.change_state(WaitForOwner)
