import logging
from datetime import datetime

from traitor.core.data.models import TradingStrategy
from traitor.core.data.repositories import TradingStrategyRepository, CoinRepository
from traitor.core.tools.ai.llm_tools.llm_tool import LLMTool
from traitor.core.tools.trading.wallet import Wallet


class CoinStateTool(LLMTool):
    name: str = "set_coin_state"
    description: str ="A tool to change the state of a coin. Coins can be activated to take them into account for trading or deactivated to ignore them."
    parameters: dict[str, str] = {
        "type": "object",
        "properties": {
            "coin": {
                "type": "string",
                "description": "The symbol or name of the coin to update.",
            },
            "active": {
                "type": "boolean",
                "description": "If the coin should be activated (True) or deactivated (False).",
            },
            "reason": {
                "type": "string",
                "description": "The reason for this action.",
            },
        },
        "required": ["coin"],
    }
    def __init__(self, wallet: Wallet | None = None):
        self.repo = CoinRepository()
        self.wallet = wallet

    # TODO: instead of directly changing the coin-state, just propose the update to the user, which can then manually activate/deactivate the coin
    # TODO: when there are multiple coins with the same symbol/name, prompt the LLM again, to choose the id which should be used
    def execute(self, coin: str, active: bool, reason: str | None = None) -> str:
        c = self.repo.try_get(coin)
        if c is None:
            return f"Coin {coin} was not found. Its state cannot be updated. It cannot be traded."
        if not c.can_trade:
            return f"The coin {coin} cannot be traded, so we cannot activate or use it."

        c.active = active
        self.repo.update(c)
        info = f"Changed state of coin {c.name} ({c.symbol}/{c.id}) to active={active}"
        logging.info(info)

        # update the wallet, if available
        if self.wallet is not None:
            if not self.wallet.contains_coin(c.id):
                self.wallet.register_coin(c)
            else:
                if active:
                    self.wallet.activate_coin(c.id)
                else:
                    self.wallet.deactivate_coin(c.id)

        return info