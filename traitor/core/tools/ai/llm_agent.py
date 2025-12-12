import abc
import json
import logging
from abc import ABC
from typing import List

from traitor.core.data.repositories.token_usage_repository import TokenUsageRepository
from traitor.core.tools.ai.llm_tools import LLMTool


def unwrap_md_json(text: str) -> str:
    if text.startswith("```json") and text.endswith("```"):
        return text[7:-3].strip()
    return text



# TODO: fine-tune reasoning effort (?)

class LLMAgent(ABC):
    name: str
    model_name: str

    def __init__(self):
        self.token_usage_repo = TokenUsageRepository()

    def __str__(self):
        return f"{self.name} ({self.model_name})"

    @abc.abstractmethod
    def process_text(self, contents: List[str], prompt_cache_key: str | None = None, usage_comment: str | None = None) -> str:
        pass

    @abc.abstractmethod
    def process_tooled(self, contents: List[str], tools: list[LLMTool] = None, prompt_cache_key: str | None = None, usage_comment: str | None = None) -> str:
        pass

    def ask_for_json(self, contents:List[str], prompt_cache_key: str | None = None, usage_comment: str | None = None) -> str:
        response = self.process_text(contents, prompt_cache_key, usage_comment)
        response = unwrap_md_json(response)
        try:
            json.loads(response)
            return response
        except:
            logging.debug("Response was not JSON. Ask again!")
            contents.append("Your previous output was not valid json! Output only valid JSON, no markdown, no extra text, no comments!")
            response = self.process_text(contents, prompt_cache_key, usage_comment+"_EnforceJson")
            response = unwrap_md_json(response)
        return response
