from .llm import LLM
import tiktoken
from openai import OpenAI, AsyncOpenAI  # Updated import
import os

# Updated client instantiation
client =  None
def get_client():
    global client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class OpenAI_LLM(LLM):

    def __init__(self,
        model: str,                     # e.g. "GPT-4"
        max_prompt_tokens: int,
        max_completion_tokens: int,
        prompt_token_cost: float,       # In dollars / 1000 tokens
        completion_token_cost: float,   # In dollars / 1000 tokens
        temperature: float | None = None,
        request_timeout = None,
        _async: bool = False,
        no_system_prompt = False,
        encoding_for_model = None,
        no_stream = False,
    ):
        encoder = tiktoken.encoding_for_model(encoding_for_model or model)
        super().__init__(
            model=model,
            max_prompt_tokens=max_prompt_tokens,
            max_completion_tokens=max_completion_tokens,
            prompt_token_cost=prompt_token_cost,
            completion_token_cost=completion_token_cost,
            encoder=encoder.encode,
            decoder=encoder.decode,
            request_timeout = request_timeout,
            _async=_async,
            no_system_prompt=no_system_prompt
        )
        self.temperature = temperature or 1.0
        self.no_stream = no_stream


    async def acall(self, messages, temperature=None, max_completion_tokens=None,
                    max_completion_words=None, num_choices=None, stream=False):
        """
        Asynchronous call to the OpenAI API.
        """
        get_client()
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

        if self.request_timeout is not None and self.request_timeout > 0:
            params['request_timeout'] = request_timeout

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
        get_client()
        stream = False if self.no_stream else stream
        if max_completion_words:
            if max_completion_tokens is not None:
                raise RuntimeError('Ambiguous request for max_response_tokens and max_response_words.')
            max_completion_tokens = int(max_completion_words * 3. / 4.)

        params = {
            'model': self.model,
            'max_completion_tokens': max_completion_tokens or self.max_completion_tokens,
            'temperature': self.temperature if temperature is None else temperature,
            'messages': messages,
        }
        if num_choices is not None:
            params['n'] = num_choices

        if self.request_timeout is not None and self.request_timeout > 0:
            params['request_timeout'] = request_timeout

        if stream:
            response = client.chat.completions.create(**params, stream=True)
            for chunk in response:
                content = chunk.model_dump()
                yield content
        else:
            response = client.chat.completions.create(**params)
            yield response.model_dump()



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


class GPT_4o_Mini(OpenAI_LLM):
    def __init__(self, _async=False, temperature=None):
        super().__init__(
            model='gpt-4o-mini',
            temperature=temperature,
            max_prompt_tokens=128000,
            max_completion_tokens=4096,
            prompt_token_cost=0.01,
            completion_token_cost=0.03,
            _async=_async
        )

class GPT_O1_Preview(OpenAI_LLM):
    def __init__(self, _async=False):
        super().__init__(
            model='o1-preview-2024-09-12',
            temperature=None,
            max_prompt_tokens=128000,
            max_completion_tokens=32768 ,
            prompt_token_cost=0.01,
            completion_token_cost=0.03,
            request_timeout=200,
            _async=_async,
            no_system_prompt = True,
            encoding_for_model='gpt-4o',
            no_stream = True,
        )

class GPT_O1_Mini(OpenAI_LLM):
    def __init__(self, _async=False):
        super().__init__(
            model='o1-mini',
            temperature=None,
            max_prompt_tokens=128000,
            max_completion_tokens=32768,
            prompt_token_cost=0.01,
            completion_token_cost=0.03,
            request_timeout=200,
            _async=_async,
            no_system_prompt = True,
            encoding_for_model='gpt-4o',
            no_stream = True,
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
