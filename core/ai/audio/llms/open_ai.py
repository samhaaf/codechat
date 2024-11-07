from .llm import LLM
import tiktoken
from openai import OpenAI, AsyncOpenAI  # Updated import
import os

# Updated client instantiation
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class OpenAI_LLM(LLM):

    def __init__(self,
        model: str,                     # e.g. "GPT-4"
        max_prompt_tokens: int,
        max_completion_tokens: int,
        prompt_token_cost: float,       # In dollars / 1000 tokens
        completion_token_cost: float,   # In dollars / 1000 tokens
        temperature: float | None = None,
        _async: bool = False,
    ):
        encoder = tiktoken.encoding_for_model(model)
        super().__init__(
            model=model,
            max_prompt_tokens=max_prompt_tokens,
            max_completion_tokens=max_completion_tokens,
            prompt_token_cost=prompt_token_cost,
            completion_token_cost=completion_token_cost,
            encoder=encoder.encode,
            decoder=encoder.decode,
            _async=_async
        )
        self.temperature = temperature or 0.3


    async def acall(self, messages, temperature=None, max_completion_tokens=None,
                    max_completion_words=None, num_choices=None, stream=False):
        """
        Asynchronous call to the OpenAI API.
        """
        if max_completion_words:
            if max_completion_tokens is not None:
                raise RuntimeError('Ambiguous request for max_response_tokens and max_response_words.')
            max_completion_tokens = int(max_completion_words * 3. / 4.)

        params = {
            'model': self.model,
            'max_tokens': max_completion_tokens or self.max_completion_tokens,
            'temperature': self.temperature if temperature is None else temperature,
            'messages': messages,
        }
        if num_choices is not None:
            params['n'] = num_choices

        if stream:
            response = await AsyncOpenAI().chat.completions.create(**params, stream=True)
        else:
            response = await AsyncOpenAI().chat.completions.create(**params)

        response_dict = response.model_dump()

        return response_dict


    def call(self, messages, temperature=None, max_completion_tokens=None,
             max_completion_words=None, num_choices=None, stream=True):
        """
        Synchronous call to the OpenAI API.
        """
        if max_completion_words:
            if max_completion_tokens is not None:
                raise RuntimeError('Ambiguous request for max_response_tokens and max_response_words.')
            max_completion_tokens = int(max_completion_words * 3. / 4.)

        params = {
            'model': self.model,
            'max_tokens': max_completion_tokens or self.max_completion_tokens,
            'temperature': self.temperature if temperature is None else temperature,
            'messages': messages,
        }
        if num_choices is not None:
            params['n'] = num_choices

        if stream:
            response = client.chat.completions.create(**params, stream=True)
            for chunk in response:
                content = chunk.model_dump()
                yield content
        else:
            raise NotImplementedError()
            # response = client.chat.completions.create(**params)
            # print('response', response)
            #
            # response_dict = response.model_dump()
            # print('response_dict', response_dict)
            #
            # return response_dict



class GPT3_5_Turbo(OpenAI_LLM):
    def __init__(self, _async=False, temperature=None):
        super().__init__(
            model='gpt-3.5-turbo',
            temperature=temperature,
            max_prompt_tokens=4000,
            max_completion_tokens=4000,
            prompt_token_cost=0.002,
            completion_token_cost=0.002,
            _async=_async
        )


class GPT4_8K(OpenAI_LLM):
    def __init__(self, _async=False, temperature=None):
        super().__init__(
            model='gpt-4',
            temperature=temperature,
            max_prompt_tokens=8000,
            max_completion_tokens=8000,
            prompt_token_cost=0.03,
            completion_token_cost=0.06,
            _async=_async
        )


class GPT4_Turbo(OpenAI_LLM):
    def __init__(self, _async=False, temperature=None):
        super().__init__(
            model='gpt-4-1106-preview',
            temperature=temperature,
            max_prompt_tokens=128000,
            max_completion_tokens=4096,
            prompt_token_cost=0.01,
            completion_token_cost=0.03,
            _async=_async
        )


class GPT_4o(OpenAI_LLM):
    def __init__(self, _async=False, temperature=None):
        super().__init__(
            model='gpt-4o',
            temperature=temperature,
            max_prompt_tokens=128000,
            max_completion_tokens=4096,
            prompt_token_cost=0.01,
            completion_token_cost=0.03,
            _async=_async
        )


class GPT4_Vision(OpenAI_LLM):
    def __init__(self, _async=False, temperature=None):
        super().__init__(
            model='gpt-4-vision-preview',
            temperature=temperature,
            max_prompt_tokens=128000,
            max_completion_tokens=4096,
            prompt_token_cost=0.01,
            completion_token_cost=0.03,
            _async=_async
        )