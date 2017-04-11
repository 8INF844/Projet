# -*- encoding: UTF-8 -*-
from core import StatesAgent
from states import OfferHelp
from naoqi import ALModule

import argparse

class BearerAssistantEventsHandler(ALModule):
    def __init__(self, name, agent):
        ALModule.__init__(self, name)
        self.agent = agent

    def on_word_recognized(self, key, value, message):
        print('Recognized')
        print(key)
        print(value)
        print(message)

    def on_touched(self, str_var_name, sensors):
        for sensor in sensors:
            if sensor[1]:
                self.agent.touched_sensors.append(sensor[0])

class BearerAssistant(StatesAgent):
    def __init__(self, ip, port):
        StatesAgent.__init__(self, ip, port=9559)
        self.words_recognized = []
        self.touched_sensors = []

    def init(self):
        self.state_machine.change_state(OfferHelp)
        # self.state_machine.change_state(WaitForOwner)



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

    # Initialize bearer assistant
    bearer_assistant = BearerAssistant(args.ip, args.port)
    # Initialize events handler
    global baeh
    baeh = BearerAssistantEventsHandler('baeh', bearer_assistant)
    bearer_assistant.start()
