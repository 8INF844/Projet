# -*- encoding: UTF-8 -*-
from core.agent import StatesAgent
from states import WaitForOwner

import argparse


class BearerAssistant(StatesAgent):
    def __init__(self, name):
        StatesAgent.__init__(self, name, WaitForOwner)
        self.face_proxy.enableTracking(False)
        self.speech_recognition.setLanguage('French')

    def init(self):
        self.state_machine.change_state(WaitForOwner)


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

    # Initialize and start bearer assistant
    global bearer_assistant
    bearer_assistant = BearerAssistant('bearer_assistant', args.ip, args.port)
    bearer_assistant.start()
