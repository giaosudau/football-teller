import os

from llama_index.llms import OpenAI


class OpenAIAPI:

    def __init__(self, model='gpt-3.5-turbo', temperature=0, max_tokens=1024):
        print(os.environ['OPENAI_API_KEY'])
        self.llm = OpenAI(model=model, temperature=temperature, max_tokens=max_tokens)
