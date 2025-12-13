from abc import ABC, abstractmethod
from typing import TypedDict, Optional

from traitor.core.data.models import Coin, CoinApiType
from traitor.core.research.market.crypto_api_base import CryptoApiBase


class ExchangeApiEndpoints(TypedDict):
    coins: str
    exchange_rates: str
    exchange_volume_bounds: str

class ExchangeRate(TypedDict):
    rate: float
    min_amount: float | None
    max_amount: float | None

class ExchangeVolumeBounds(TypedDict):
    min_amount: float | None
    max_amount: float | None

class CryptoExchangeApi(CryptoApiBase, ABC):
    api_type = CoinApiType.EXCHANGE
    apis: ExchangeApiEndpoints

    @abstractmethod
    def _get_exchange_volume_bounds(self, out_id: str, in_id: str, fixed: bool) -> ExchangeVolumeBounds | None:
        pass

    @abstractmethod
    def _get_exchange_rate(self, out_id: str, in_id: str, fixed: bool) -> float | None:
        pass

    def get_exchange_rate(self, coin_out: Coin, coin_in: Coin, fixed: bool = False, fallback_to_symbols: bool = True) -> ExchangeRate | None:
        if not (coin_out.can_trade and coin_in.can_trade):
            return None

        out_id = coin_out.get_api(self.name)
        in_id = coin_in.get_api(self.name)

        if out_id is not None:
            out_id = out_id.api_coin_id
        elif out_id is None and fallback_to_symbols:
            out_id = coin_out.symbol

        if in_id is not None:
            in_id = in_id.api_coin_id
        elif in_id is None and fallback_to_symbols:
            in_id = coin_in.symbol

        if out_id is None or in_id is None:
            return None
        exchange_rate = self._get_exchange_rate(out_id, in_id, fixed)
        if exchange_rate is None:
            return None

        exchange_volume_bounds = self._get_exchange_volume_bounds(out_id, in_id, fixed)
        result: dict[str, float] = {
            "rate": exchange_rate,
        }
        if exchange_volume_bounds is not None:
            for k in exchange_volume_bounds.keys():
                result[k] = exchange_volume_bounds[k]
        return result