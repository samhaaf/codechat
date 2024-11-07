import random

class StateMachine(metaclass=StateMachineMeta):
    def __init__(self, state=None):
        self._state = state
        self._terminal = False

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        assert new_state in self._state_handlers, (
            f'Attempted to go to state {new_state} without a handler'
        )
        self._state = new_state

    @property
    def terminal(self):
        return self._terminal

    def kill(self):
        self._terminal = True

    def get_handler(self):
        handlers = self._state_handlers.get(self.state, [])
        total_rate = sum(h.rate for h in handlers)
        r = random.uniform(0, total_rate)
        upto = 0
        for h in handlers:
            if upto + h.rate >= r:
                return h
            upto += h.rate

    def run(self, timeout=None):
        while not self.terminal:
            handler = self.get_handler()
            if handler:
                handler(self)


class StateMachineMeta(type):
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        cls._state_handlers = {}
        for m in dct:
            if callable(dct[m]) and hasattr(dct[m], 'state'):
                method = dct[m]
                state = method.state
                if state not in cls._state_handlers:
                    cls._state_handlers[state] = []
                cls._state_handlers[state].append(method)
                if len(cls._state_handlers[state]) > 1 and any(h.rate is None for h in cls._state_handlers[state]):
                    raise ValueError(
                        f"All handlers for state '{state}' must have a rate, "
                        "since there are multiple handlers"
                    )


def handler(state, rate=None):
    def wrapper(function):
        function.state = state
        function.rate = rate
        return function
    return wrapper
