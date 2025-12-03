from typing import List

from PIL.Image import Image
from dependency_injector.wiring import inject, Provide
from openai import OpenAI


from traitor.core.tools.ai.llm_agent import LLMAgent


class LLMOpenAI(LLMAgent):
    name = "OpenAI"

    @inject
    def __init__(self, model: str = "gpt-5-nano", api_key: str = Provide["config.API_KEYS.OPENAI"]):
        self.model_name = model
        self.client = OpenAI(api_key=api_key)

    def process_text(self, contents: List[str]) -> str:
        raise NotImplementedError("TODO: Fix OpenAI implementation")
        response = self.client.responses.create(
            model=self.model_name,
            input=contents,
            service_tier="flex"
        )
        return response.out_text

    def process_image(self, image: Image, context: List[str]) -> str:
        raise NotImplementedError("TODO: Fix OpenAI implementation")
