from abc import ABC, abstractmethod
from datetime import datetime

from traitor.core.data.models import Price, Coin, CoinApiType, CoinUrl
from traitor.core.research.market.crypto_api_base import CryptoApiBase


class CryptoInfoApi(CryptoApiBase):
    api_type = CoinApiType.INFO

    @abstractmethod
    def get_current_prices(self, coins: list[Coin]) -> list[Price]:
        """
        Get the current price for a list of coins
        :return:
        """
        pass

    @abstractmethod
    def get_coin_historical_prices(self,
                                   coin: Coin,
                                   t_from: datetime = None,
                                   t_to: datetime = None
                                   ) -> list[Price]:
        """
        Get the historical prices for a given coin
        :param coin:
        :param t_from: Timestamp from when to start getting prices. If None -> Today - 365
        :param t_to:  Timestamp to when to get the prices. If None -> Today
        :return:
        """
        pass

    @abstractmethod
    def update_coin_info(self, coin: Coin) -> tuple[Coin, list[CoinUrl]]:
        """
        update generic information of a coin
        :param coin:
        :return: updated Coin
        """
        pass
