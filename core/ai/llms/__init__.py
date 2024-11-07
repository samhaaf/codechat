from .open_ai import (
    GPT3_5_Turbo, GPT4_8K, GPT4_Turbo, GPT_4o, GPT_4o_Mini, GPT_O1_Preview,
    GPT_O1_Mini, GPT4_Vision
)

models = {
    'gpt4': GPT4_8K,
    'gpt4-turbo': GPT4_Turbo,
    '4o': GPT_4o,
    'gpt-4o': GPT_4o,
    'gpt-4o-mini': GPT_4o_Mini,
    'o1': GPT_O1_Preview,
    'o1-preview': GPT_O1_Preview,
    'o1-mini': GPT_O1_Mini,
    'gpt4-vision': GPT4_Vision,
    'gpt3.5-turbo': GPT3_5_Turbo
}
