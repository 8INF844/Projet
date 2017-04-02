# -*- encoding: UTF-8 -*-
''' Say `My {Body_part} is touched` when receiving a touch event
'''

import almath
import math
import motion
import sys
import time

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
import argparse

# Global variable to store the AgentNao module instance
AgentNao = None

def StiffnessOn(proxy):
    #We use the "Body" name to signify the collection of all joints
    pNames = "Body"
    pStiffnessLists = 1.0
    pTimeLists = 1.0
    proxy.stiffnessInterpolation(pNames, pStiffnessLists, pTimeLists)

class Module(ALModule):
    ''' A simple module able to react
        to touch events.
    '''
    def __init__(self, name):
        ALModule.__init__(self, name)

        self.tts = ALProxy('ALTextToSpeech')
        self.face_proxy = ALProxy('ALFaceDetection')
        self.memory = ALProxy('ALMemory')
        self.motion_proxy  = ALProxy('ALMotion')
        self.posture_proxy = ALProxy('ALRobotPosture')
        self.speech_recognition = ALProxy('ALSpeechRecognition')
        self.speech_recognition.setLanguage('English')
        self.has_obj = False

        # Subscribe to TouchChanged event:
        self.memory.subscribeToEvent('TouchChanged',
            'AgentNao',
            'onTouched')

    def say(self, text):
        self.tts.say(text)

    def face_suscribe(self):
        period = 500
        self.face_proxy.subscribe('Test_Face', period, 0.0 )

    def detect_face(self):
        memValue = 'FaceDetected'
        time.sleep(0.5)
        val = self.memory.getData(memValue)

        try:
            if(val and isinstance(val, list) and len(val) >= 2):
                face_info_array = val[1]
                list_faces = []
                # get pos for each face detected
                for j in range(len(face_info_array) - 1):
                    face_info = face_info_array[j]
                    list_faces.append(face_info[0])
                return list_faces
        except Exception, e:
            pass
        # no face detected
        return None

    def face_unsuscribe(self):
        self.face_proxy.unsubscribe('Test_Face')

    def stand_up(self):
        self.motion_proxy.wakeUp()
        self.posture_proxy.goToPosture('StandInit', 0.5)

    def sit(self):
        self.motion_proxy.wakeUp()
        self.posture_proxy.goToPosture('Sit', 0.5)

    def detect_word(self, vocabulary):
        self.speech_recognition.setVocabulary(vocabulary, False)

        self.memory.subscribeToEvent('WordRecognized',
            'AgentNao',
            'onWordRecognized')
        # TODO self.memory.subscribeToEvent
        print(self.speech_recognition.getLanguage())
        self.speech_recognition.subscribe('Test_ASR')
        print('Speech recognition engine started')
        time.sleep(5)
        #words_recognized = self.memory.getData('WordRecognized')
        print(words_recognized)
        self.speech_recognition.unsubscribe('Test_ASR')
        #return words_recognized

    def onWordRecognized(self, key, value, message):

        self.memory.unsubscribeToEvent('WordRecognized',
            'AgentNao')
        print("Recognized")
        print(key)
        print(value)
        print(message)
        self.memory.subscribeToEvent('WordRecognized',
            'AgentNao',
            'onWordRecognized')


    def onTouched(self, strVarName, value):
        ''' This will be called each time a touch
        is detected.

        '''
        # Unsubscribe to the event when talking,
        # to avoid repetitions
        self.memory.unsubscribeToEvent('TouchChanged',
            'AgentNao')

        touched_bodies = []
        for p in value:
            if p[1]:
                touched_bodies.append(p[0])

        self.close_hand(touched_bodies)

        # Subscribe again to the event
        self.memory.subscribeToEvent('TouchChanged',
            'AgentNao',
            'onTouched')

    def close_hand(self, bodies):
        if (bodies == []):
            return
        print(bodies)

        if bodies[0] == "RArm":
            self.motion_proxy.closeHand('RHand')
            self.has_obj = True

    def grab_object(self):
        self.motion_proxy.wakeUp()
        # Set NAO in Stiffness On
        StiffnessOn(self.motion_proxy)

        # Send NAO to Pose Init
        self.posture_proxy.goToPosture("StandInit", 0.5)

        effector   = "RArm"
        space      = motion.FRAME_ROBOT
        axisMask   = almath.AXIS_MASK_VEL    # just control position
        isAbsolute = False

        # Since we are in relative, the current position is zero
        currentPos = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        # Define the changes relative to the current position
        dx         =  0.05      # translation axis X (meters)
        dy         =  0.0      # translation axis Y (meters)
        dz         =  0.2      # translation axis Z (meters)
        dwx        =  0.00      # rotation axis X (radians)
        dwy        =  0.00      # rotation axis Y (radians)
        dwz        =  0.00      # rotation axis Z (radians)
        targetPos  = [dx, dy, dz, dwx, dwy, dwz]

        # Go to the target and back again # TODO stay in position
        path       = [targetPos, targetPos, targetPos, currentPos]
        times      = [2.0, 4.0, 6.0, 8.0] # seconds

        self.motion_proxy.openHand('RHand')
        self.motion_proxy.positionInterpolation(effector, space, path,
                                          axisMask, times, isAbsolute)

    def drop_object(self):
        self.motion_proxy.wakeUp()
        self.motion_proxy.openHand('RHand')
        self.has_obj = False

    def move_to_other(self):
        self.motion_proxy.moveTo(0, 0, math.pi)
        self.motion_proxy.moveTo(0.2, 0, 0)


def main(ip, port):
    ''' Main entry point
    '''
    # We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    broker = ALBroker('broker',
       '0.0.0.0',   # listen to anyone
       0,           # find a free port and use it
       ip,          # parent broker IP
       port)        # parent broker port


    global AgentNao
    AgentNao = Module('AgentNao')
    AgentNao.grab_object()
    time.sleep(1000)
    client_found = False
    print('wake up')
    AgentNao.say('Bonjour')
    while not client_found:
        AgentNao.sit()
        # Chercher quelqu'un (facial reco)
        print('try to find a client')
        AgentNao.face_suscribe()
        clients = []
        while len(clients) is 0:
            detected = AgentNao.detect_face()
            if detected:
                clients = detected
        AgentNao.face_unsuscribe()
        # Se lever
        print('ask the client')
        AgentNao.stand_up()
        # Aller le voir
        # TODO
        # Lui demander si il veut une boisson
        AgentNao.say('Puis-je prendre un objet ?')

        # Si oui prendre commande
        client_found = True
        # TODO
        vocabulary = ['yes', 'no']
        words_recognized = AgentNao.detect_word(vocabulary)
        if words_recognized and words_recognized[0] == 'yes':
            client_found = True
            AgentNao.say('Que voulez-vous ?')
        else:
            AgentNao.say('D\'accord')


    AgentNao.grab_object()
    while not AgentNao.has_obj:
        time.sleep(1)

    AgentNao.move_to_other()
    AgentNao.drop_object()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print
        print 'Interrupted by user, shutting down'
        broker.shutdown()
        sys.exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str, default='169.254.76.111',
                        help='Robot ip address')
    parser.add_argument('--port', type=int, default=9559,
                        help='Robot port number')
    args = parser.parse_args()
    main(args.ip, args.port)
