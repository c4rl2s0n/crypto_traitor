from abc import ABC, abstractmethod
from typing import TypedDict

from traitor.core.data.models import Coin, CoinApiType
from traitor.core.research.market.crypto_api_base import CryptoApiBase


class ExchangeApiEndpoints(TypedDict):
    coins: str
    exchange_rates: str

class CryptoExchangeApi(CryptoApiBase, ABC):
    api_type = CoinApiType.EXCHANGE
    apis: ExchangeApiEndpoints

    @abstractmethod
    def _get_exchange_rate(self, out_id: str, in_id: str, fixed: bool) -> float | None:
        pass

    def get_exchange_rate(self, coin_out: Coin, coin_in: Coin, fixed: bool = False, fallback_to_symbols: bool = True) -> float | None:
        out_id = coin_out.get_api(self.name)
        in_id = coin_in.get_api(self.name)

        if out_id is None and fallback_to_symbols:
            out_id = coin_out.symbol
        if in_id is None and fallback_to_symbols:
            in_id = coin_in.symbol

        if out_id is None or in_id is None:
            return None
        return self._get_exchange_rate(out_id, in_id, fixed)