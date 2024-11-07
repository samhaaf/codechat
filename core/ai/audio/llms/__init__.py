from .open_ai import GPT3_5_Turbo, GPT4_8K, GPT4_Turbo, GPT_4o, GPT4_Vision

models = {
    'gpt4': GPT4_8K,
    'gpt4-turbo': GPT4_Turbo,
    'gpt-4o': GPT_4o,
    'gpt4-vision': GPT4_Vision,
    'gpt3.5-turbo': GPT3_5_Turbo
}
