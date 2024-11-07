from abc import ABCMeta, abstractmethod
import copy
from threading import Event


class Session:
    def __init__(self, model, _async=False):
        self.model = model
        self._async = _async
        self._terminal_event = Event()
        self._history = []
        self._constraints = []
        self._usage = {
            'prompt_tokens': 0,
            'completion_tokens': 0,
            'total_tokens': 0
        }
        self.model._register_session(self, self._terminal_event)

    @property
    def usage(self):
        usage = copy.copy(self._usage)
        usage['prompt_dollars'] = self.model.prompt_token_cost * usage['prompt_tokens']
        usage['completion_dollars'] = self.model.completion_token_cost * usage['completion_tokens']
        usage['total_dollars'] = usage['prompt_dollars'] + usage['completion_dollars']
        return usage

    @property
    def history(self):
        return [self._get_system_message()] + copy.deepcopy(self._history)

    def kill(self):
        self._terminal_event.set()

    @property
    def terminal(self):
        return self._terminal_event.is_set()

    def _get_system_message(self):
        system_message = "You are an AI assistant."
        for constraint in self._constraints:
            constraint = constraint.strip()
            while constraint[-1] == '.':
                constraint = constraint[:-1]
            system_message += ' ' + constraint + '.'
        return {
            "role": "system",
            "content": system_message
        }

    def constrain(self, constraint):
        self._constraints.append(constraint)

    def _is_pending_choice(self):
        return self._history and isinstance(self._history[-1], (list, tuple))

    def choose(self, choice: int):
        if not self._is_pending_choice():
            raise RuntimeError(
                'Attempted to call session.choose(choice: int) when a choice was not needed'
            )
        if -1 <= choice >= len(self._history[-1]):
            raise RuntimeError(
                f'Expected choice between 0 and {len(self._history[-1]) - 1}, got {choice}.'
            )
        self._history[-1] = self._history[-1][choice]


    def call(self, message, num_choices=None, **params):
        if self._is_pending_choice():
            raise RuntimeError(
                'Attempted to continue session without choosing the best last sample. '
                'Use Session.choose(choice: int)'
            )

        new_history = self.history + [{
            "role": "user",
            "content": message
        }]

        # if stream:
        response_stream = self.model.call(
            messages=new_history,
            num_choices=num_choices,
            stream=True,
            **params
        )
        full_response_content = ""
        for chunk in response_stream:
            content = chunk['choices'][0]['delta']['content']
            if content is None:
                new_history.append({
                    "role": "assistant",
                    "content": full_response_content
                })
                self._history += new_history[-2:] # TODO see next todo
            else:
                full_response_content += content
            # TODO incrementally update history here, for intended interrupts

            yield chunk

        # Once streaming is complete, update history with the full response


        # else:
        #     # Handle non-streaming calls as before
        #     response = self.model.call(
        #         messages=new_history,
        #         num_choices=num_choices,
        #         **params
        #     )
        #     print('response 2', response)
        #     for k,v in response['usage'].items():
        #         self._usage[k] = self._usage.get(k, 0) + v
        #     choices = response['choices']
        #     print('choices', choices)
        #     if num_choices is not None:
        #         new_history.append([choice['message'] for choice in choices])
        #         response = [choice['message']['content'] for choice in choices]
        #     else:
        #         new_history.append(choices[0]['message'])
        #         response = choices[0]['message']['content']
        #     print('new_history', new_history)
        #     print('resp', response)
        #     self._history += new_history[-2:]
        #     return response


class LLM(metaclass=ABCMeta):

    Session = Session

    @abstractmethod
    def __init__(self,
        model: str,                     # e.g. "GPT-4"
        max_prompt_tokens: int,
        max_completion_tokens: int,
        prompt_token_cost: float,       # In dollars / 1000 tokens
        completion_token_cost: float,   # In dollars / 1000 tokens
        encoder: callable,
        decoder: callable,
        _async: bool = False,
    ):
        self.model = model
        self.max_prompt_tokens = max_prompt_tokens
        self.max_completion_tokens = max_completion_tokens
        self.prompt_token_cost = prompt_token_cost
        self.completion_token_cost = completion_token_cost
        self._async = _async
        self._sessions = []
        self.encoder = encoder

    @abstractmethod
    def call(self, stream=False, **kwargs) -> dict:
        pass


    @abstractmethod
    async def acall(self, stream=False, **kwargs) -> dict:
        pass

    def kill(self) -> None:
        for session in self._sessions:
            session['terminal_event'].set()

    def get_session(self, _async=None) -> Session:
        _async = _async or self._async
        return self.Session(self)

    def _register_session(self, session, terminal_event) -> None:
        self._sessions.append({
            'session': session,
            'terminal_event': terminal_event
        })

    @property
    def usage(self) -> dict:
        usage = {}
        for session in self._sessions:
            for k,v in session.usage.items():
                usage[k] = usage.get(k, 0) + v
        return usage

    def tokenize(self, text):
        return self.encoder(text)

    def count_tokens(self, text):
        return len(self.tokenize(text))

    def count_file_tokens(self, path, cache=True):

        with open(path) as f:
            return self.count_tokens(f.read().strip())
