import logging
from typing import TypedDict

from traitor.core.data.models import Coin
from traitor.core.data.repositories import PricesRepository
from traitor.core.tools.trading.wallet import Wallet


class PaperRun(object):
    def __init__(self, initial_balance: Wallet):
        self.wallet = initial_balance
        self.price_repo = PricesRepository()
        self.value_history = [self.wallet.total_value()]
        self.trade_log = []

    def trade(self, coin_out: Coin, coin_in: Coin, balance_out: float, balance_in: float) -> bool:
        if not self.wallet.verify_trade(coin_out, coin_in, balance_out):
            logging.warn("Tried to perform invalid trade")
            return False
        coin_out_price = self.price_repo.get_last_price(coin_out.id)
        coin_in_price = self.price_repo.get_last_price(coin_in.id)

        _trade = {
            "out": {
                "coin": coin_out.name,
                "balance": balance_out,
                "coin_value": coin_out_price.value if coin_out_price is not None else None,
            },
            "in": {
                "coin": coin_in.name,
                "balance": balance_in,
                "coin_value": coin_in_price.value if coin_in_price is not None else None,
            },
        }
        self.trade_log.append(_trade)
        self.wallet.remove(coin_out, balance_out)
        self.wallet.add(coin_in, balance_in)
        logging.info(f"Trade performed.\nPortfolio: {self.wallet.portfolio_str()}\nTotal value of the wallet: {self.wallet.total_value()}")
        return True