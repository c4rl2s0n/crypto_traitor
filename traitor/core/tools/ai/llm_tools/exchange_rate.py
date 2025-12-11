from datetime import datetime

from traitor.core.data.models import TradingStrategy, Coin
from traitor.core.data.repositories import TradingStrategyRepository, CoinRepository
from traitor.core.research.market.exchange_api import CryptoExchangeApi
from traitor.core.tools.ai.llm_tools.llm_tool import LLMTool


class ExchangeRateTool(LLMTool):
    name: str = "get_exchange_rate"
    description: str ="A tool to query the current exchange rate."
    parameters: dict[str, str] = {
        "type": "object",
        "properties": {
            "coin_out": {
                "type": "string",
                "description": "The id of the currency to spend/trade for another. It can be the Name of Symbol of the currency.",
            },
            "coin_in": {
                "type": "string",
                "description": "The id of the currency to receive in the trade. It can be the Name of Symbol of the currency.",
            },
            "fixed": {
                "type": "boolean",
                "description": "True: the exchange rate will be provided as a fixed value. This usually results in a worse rate, but provides security that this exact rate applies",
            },
        },
        "required": ["coin_out", "coin_in"],
    }
    def __init__(self, api: CryptoExchangeApi):
        self.api = api
        self.coin_repo = CoinRepository()

    def execute(self, coin_out: str, coin_in: str, fixed: bool = False) -> float | str:
        c_out = self.coin_repo.try_get(coin_out, active_only=True)
        c_in = self.coin_repo.try_get(coin_in, active_only=True)
        if c_out is None:
            return f"No coin found with name or symbol {coin_out}"
        if c_in is None:
            return f"No coin found with name or symbol {coin_in}"
        return self.api.get_exchange_rate(c_out, c_in, fixed)
