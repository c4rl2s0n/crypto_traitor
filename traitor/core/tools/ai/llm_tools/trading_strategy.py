from datetime import datetime

from traitor.core.data.models import TradingStrategy
from traitor.core.data.repositories import TradingStrategyRepository
from traitor.core.tools.ai.llm_tools.llm_tool import LLMTool


class TradingStrategyTool(LLMTool):
    name: str = "set_trading_strategy"
    description: str ="A tool to change the current trading strategy."
    parameters: dict[str, str] = {
        "type": "object",
        "properties": {
            "strategy": {
                "type": "string",
                "description": "The new trading strategy to use.",
            },
            "reason": {
                "type": "string",
                "description": "The reason for choosing this strategy.",
            },
        },
        "required": ["strategy"],
    }
    def __init__(self):
        self.repo = TradingStrategyRepository()

    def execute(self, strategy: str, reason: str | None = None):
        self.repo.add(
            TradingStrategy(
                strategy=strategy,
                reason=reason,
                time=datetime.now(),
            )
        )