import abc
import json
import logging
from abc import ABC
from typing import List, Callable

from PIL.Image import Image

from traitor.core.tools.ai.llm_tools import LLMTool


def unwrap_md_json(text: str) -> str:
    if text.startswith("```json") and text.endswith("```"):
        return text[7:-3].strip()
    return text


class LLMAgent(ABC):
    name: str
    model_name: str

    def __str__(self):
        return f"{self.name} ({self.model_name})"

    @abc.abstractmethod
    def process_text(self, contents: List[str]) -> str:
        pass

    @abc.abstractmethod
    def process_tooled(self, contents: List[str], tools: list[LLMTool] = None) -> str:
        pass

    def ask_for_json(self, contents:List[str]) -> str:
        response = self.process_text(contents)
        response = unwrap_md_json(response)
        try:
            json.loads(response)
            return response
        except:
            logging.debug("Response was not JSON. Ask again!")
            contents.append("Your previous output was not valid json! Output only valid JSON, no markdown, no extra text, no comments!")
            response = self.process_text(contents)
            response = unwrap_md_json(response)
        return response
