from typing import List

from PIL.Image import Image
from openai import OpenAI

from traitor.config.bootstrap import Container
from traitor.tools.ai.llm_agent import LLMAgent


class LLMOpenAI(LLMAgent):
    def __init__(self, model: str = "gpt-5-nano"):
        self.model = model
        self.client = OpenAI(api_key=Container().config.API_KEYS.OPENAI)

    def process_text(self, contents: List[str]) -> str:
        raise NotImplementedError("TODO: Fix OpenAI implementation")
        response = self.client.responses.create(
            model=self.model,
            input=contents,
            service_tier="flex"
        )
        return response.out_text

    def process_image(self, image: Image, context: List[str]) -> str:
        raise NotImplementedError("TODO: Fix OpenAI implementation")
