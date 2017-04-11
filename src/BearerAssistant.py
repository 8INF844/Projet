# -*- encoding: UTF-8 -*-
from core import StatesAgent
from states import OfferHelp

import argparse


class BearerAssistant(StatesAgent):
    def __init__(self, name, ip, port=9559):
        StatesAgent.__init__(self, name, ip, port=9559)
        self.words_recognized = []

    def init(self):
        self.state_machine.change_state(OfferHelp)
        # self.state_machine.change_state(WaitForOwner)

    def on_word_recognized(self, key, value, message):
        self.memory.unsubscribeToEvent('WordRecognized', 'AgentNao')
        print('Recognized')
        print(key)
        print(value)
        print(message)


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument(
        '--ip',
        type=str,
        default='192.168.0.1',
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
