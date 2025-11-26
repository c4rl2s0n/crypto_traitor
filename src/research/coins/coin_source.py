from abc import ABC, abstractmethod
from typing import List

from src.data.models import Coin


class CoinSource(ABC):
    name: str
    url_base: str

    @abstractmethod
    def get_coins(self) -> List[Coin]:
        pass
