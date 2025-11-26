from typing import List
import google.generativeai as genai
from PIL.Image import Image

from src.tools.ai.llm_agent import LLMAgent


class LLMGemini(LLMAgent):

    def __init__(self, model: str = 'gemini-2.5-flash'):
        self.model = genai.GenerativeModel(model)

    def process_text(self, contents: List[str]) -> str:
        response = self.model.generate_content(
            contents,
            stream=True
        )
        response.resolve()
        return response.text

    def process_image(self, image: Image, context: List[str]) -> str:
        content = []
        content.extend(context)
        content.append(image)
        response = self.model.generate_content(
            content,
            stream=True
        )
        response.resolve()
        return response.text
