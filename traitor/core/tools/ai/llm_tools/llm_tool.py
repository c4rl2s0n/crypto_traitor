from abc import ABC, abstractmethod

from traitor.core.tools.misc import dict_to_json




class LLMTool(ABC):
    name: str
    description: str
    parameters: dict[str, str]

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }

    def to_dict_str(self) -> str:
        return dict_to_json(self.to_dict())

    @abstractmethod
    def execute(self, *args):
        pass