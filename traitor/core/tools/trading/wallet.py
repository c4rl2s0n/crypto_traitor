import logging
from abc import ABC
from typing import TypedDict

from traitor.core.data.models import Coin
from traitor.core.data.repositories import CoinRepository, PricesRepository
from traitor.core.tools import dict_to_json


class Wallet(object):
    portfolio: dict[int, float]

    def __init__(self):
        self.coin_repo = CoinRepository()
        self.price_repo = PricesRepository()
        self.portfolio = {}

    def portfolio_str(self) -> str:
        coins = self.coin_repo.get_by_ids(list(self.portfolio.keys()))
        return dict_to_json({c.symbol:self.portfolio[c.id] for c in coins})

    def register_coin(self, coin: Coin):
        if not coin.id in self.portfolio:
            self.portfolio[coin.id] = 0

    def add(self, coin: Coin, amount: float):
        if coin.id in self.portfolio:
            self.portfolio[coin.id] += amount
        else:
            logging.warn(f"Trying to add balance to wallet for unsupported coin ({coin.name})")

    def remove(self, coin: Coin, amount: float):
        if coin.id in self.portfolio:
            self.portfolio[coin.id] -= amount
        else:
            logging.warn(f"Trying to remove balance from wallet for unsupported coin ({coin.name})")

    def verify_trade(self, coin_out: Coin, coin_in: Coin, balance_out: float):
        return coin_out.id in self.portfolio and self.portfolio[coin_out.id] >= balance_out and coin_in.id in self.portfolio

    def total_value(self):
        total = 0
        for coin_id in self.portfolio.keys():
            last_price = self.price_repo.get_last_price(coin_id)
            if last_price is None:
                continue
            total += self.portfolio[coin_id] * last_price.value
        return total