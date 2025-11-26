from datetime import datetime
from typing import List

from bs4 import BeautifulSoup

from data.models import Article, NewsSourceCategory, Coin
from research.coins.coin_source import CoinSource
from research.news.news_source import NewsSource
from tools import scraper


class CoinMarketCap(CoinSource):
    name = "CoinMarketCap"
    url_base = "https://coinmarketcap.com"

    def get_coins(self) -> List[Coin]:
        path = "/coins/views/all/"
        return scraper.extract(self.url_base + path, self._parse_coins)

    def _parse_coins(self, soup: BeautifulSoup) -> List[Coin]:
        coins = []
        i = 0
        rows = soup.find("tbody").find_all("tr")
        for row in rows:
            a = row.find_all("td")[1].find_all("a")[-1]
            name = a.text
            url = self.url_base + a["href"]
            tag = row.find_all("td")[2].text
            if tag is None or len(tag) == 0:
                # TODO: extract images as well?
                print(f"[{i+1} / {len(rows)}] Lookup tag for {name}")
                tag = self.scraper.extract(url, lambda s: s.find(attrs={"data-role": "coin-symbol"}).text)
            c = Coin(tag=tag, name=name, url_coinmarketcap=url, active=i < 15)
            coins.append(c)
            i += 1
        return coins
