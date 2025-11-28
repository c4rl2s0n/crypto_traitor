import abc
from abc import ABC
from typing import List

from PIL.Image import Image


class LLMAgent(ABC):
    @abc.abstractmethod
    def process_text(self, contents: List[str]) -> str:
        pass

    @abc.abstractmethod
    def process_image(self, image: Image, context: List[str]) -> str:
        pass