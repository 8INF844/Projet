

class StateMachine():
    """
    A standard state machine.
    """
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
    """
    The state interface.
    """
    @staticmethod
    def enter(instance):
        pass

    @staticmethod
    def process(instance):
        pass

    @staticmethod
    def process(instance):
        pass
