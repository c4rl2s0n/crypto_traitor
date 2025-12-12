import logging

from traitor.core.data.models import Coin
from traitor.core.data.repositories import CoinRepository, PricesRepository
from traitor.core.tools.misc import dict_to_json


class Wallet(object):
    portfolio: dict[int, Coin]

    def __init__(self):
        self.coin_repo = CoinRepository()
        self.price_repo = PricesRepository()
        coins = self.coin_repo.get_active()
        self.portfolio = {c.id:c for c in coins}

    def portfolio_str(self) -> str:
        coins = self.coin_repo.get_by_ids(list(self.portfolio.keys()))
        return dict_to_json({c.symbol:self.portfolio[c.id].balance for c in coins})

    def _update_coin(self, coin_id: int):
        if self.contains_coin(coin_id):
            self.coin_repo.update(self.portfolio[coin_id])

    def register_coin(self, coin: Coin):
        if not coin.id in self.portfolio:
            self.portfolio[coin.id] = coin

    def activate_coin(self, coin_id: int):
        if coin_id in self.portfolio:
            self.portfolio[coin_id].active = True
            self._update_coin(coin_id)

    def deactivate_coin(self, coin_id: int):
        if coin_id in self.portfolio:
            self.portfolio[coin_id].active = False
            self._update_coin(coin_id)

    def contains_coin(self, coin_id: int) -> bool:
        return coin_id in self.portfolio

    def can_trade_coin(self, coin_id: int) -> bool:
        return self.contains_coin(coin_id) and self.portfolio[coin_id].active and self.portfolio[coin_id].can_trade

    def add(self, coin_id: int, amount: float):
        if self.contains_coin(coin_id):
            self.portfolio[coin_id].balance += amount
            self._update_coin(coin_id)
        else:
            logging.warn(f"Trying to add balance to wallet for unsupported coin ({coin_id})")

    def remove(self, coin_id: int, amount: float):
        if self.contains_coin(coin_id):
            self.portfolio[coin_id].balance -= amount
            self._update_coin(coin_id)
        else:
            logging.warn(f"Trying to remove balance from wallet for unsupported coin ({coin_id})")

    def verify_trade(self, coin_out_id: int, coin_in_id: Coin, balance_out: float):
        return (self.can_trade_coin(coin_out_id)
                and self.portfolio[coin_out_id].balance >= balance_out
                and self.can_trade_coin(coin_in_id))

    def total_value(self):
        total = 0
        for coin in self.portfolio.values():
            last_price = self.price_repo.get_last_price(coin.id)
            if last_price is None:
                continue
            total += coin.balance * last_price.value
        return total