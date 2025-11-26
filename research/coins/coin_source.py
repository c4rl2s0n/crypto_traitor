from abc import ABC, abstractmethod
from typing import List

from bs4 import BeautifulSoup

from data.models import Article, NewsSourceCategory, Coin


class CoinSource(ABC):
    name: str
    url_base: str

    @abstractmethod
    def get_coins(self) -> List[Coin]:
        pass
