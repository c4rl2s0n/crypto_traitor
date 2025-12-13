from datetime import datetime

from dependency_injector.wiring import inject, Provide

from traitor.core.data.models import TradingStrategy
from traitor.core.data.repositories import TradingStrategyRepository, CoinRepository
from traitor.core.research.market.apis.stealthexchange import StealthexApi
from traitor.core.research.market.exchange_api import CryptoExchangeApi
from traitor.core.tools.ai.llm_tools.llm_tool import LLMTool
from traitor.core.tools.trading.paper_run import PaperRun


class TradingTool(LLMTool):
    name: str = "perform_trade"
    description: str ="A tool to trade a cryptocurrency for another one."
    parameters: dict[str, str] = {
        "type": "object",
        "properties": {
            "coin_out": {
                "type": "string",
                "description": "The symbol or name of the coin to send.",
            },
            "coin_in": {
                "type": "string",
                "description": "The symbol or name of the coin to receive.",
            },
            "amount_out": {
                "type": "number",
                "description": "The amount of the outgoing currency to trade. This cannot be more than the available balance for coin_out!",
            },
            "reason": {
                "type": "string",
                "description": "The reason, why you want to perform this trade.",
            },
            "fixed": {
                "type": "boolean",
                "description": "If the trade should be applied at a fixed rate. Fixed rate usually has worse ratio but security to get that rate. Floating trades will be performed to the actual price at the moment the trade is performed. Default: False -> trade to floating value.",
            },
        },
        "required": ["coin_out", "coin_in", "amount_out"],
    }
    @inject
    def __init__(self, network: PaperRun, crypto_exchange_api: CryptoExchangeApi = Provide["crypto_exchange_api"]):
        self.coin_repo = CoinRepository()
        self.network = network
        self.exchange_api = crypto_exchange_api

    def execute(self, coin_out: str, coin_in: str, amount_out: float, reason: str, fixed: bool = False) -> str:
        c_out = self.coin_repo.try_get(coin_out, active_only=True)
        c_in = self.coin_repo.try_get(coin_in, active_only=True)

        if c_out is None:
            return f"No coin found with name or symbol {coin_out}"
        if c_in is None:
            return f"No coin found with name or symbol {coin_in}"

        rate = self.exchange_api.get_exchange_rate(c_out, c_in, fixed=fixed)
        if rate is None:
            return "Could not obtain exchange rate for the given coins"
        if (rate["min_amount"] is not None and rate["min_amount"] > amount_out
                or rate["max_amount"] is not None and rate["max_amount"] < amount_out):
            return f"Given amount ({amount_out}) is not in the required range [{rate["min_amount"], rate["max_amount"]}]"

        self.network.trade(c_out, c_in, amount_out, amount_out * rate["rate"], reason)
        return "Trade performed."


