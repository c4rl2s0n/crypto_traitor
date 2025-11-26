import json
from datetime import datetime

import requests
from requests import Response

from src.data.models import Price, Coin
from src.tools import api_b, urljoin


class CoinGecko(object):
    base_url: str = "https://api.coingecko.com/api/v3/"
    request_count: dict[datetime, int] = {}

    currency = "usd"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _request(self, api: str) -> Response:
        headers = {
            "x-cg-demo-api-key": self.api_key,
        }
        self._count_request()
        response = requests.get(urljoin(self.base_url, api), headers=headers, timeout=10)
        self._check_response_code(response)
        return response

    def _check_response_code(self, response: Response):
        """
        Check the response code according to https://docs.coingecko.com/docs/common-errors-rate-limit
        :param response:
        :return:
        """
        if response.status_code == 401:
            # access denied
            pass
        elif response.status_code == 429:
            # too many requests; probably exceeded rate limit
            # TODO: somehow reschedule
            pass
        elif response.status_code == 10002:
            # missing API key
            pass
        elif response.status_code == 10010 or response.status_code == 10011:
            # invalid API key
            pass
        # TODO: maybe raise exceptions?

    def _count_request(self):
        now = datetime.now().replace(second=0, microsecond=0)
        if now not in self.request_count:
            self.request_count[now] = 1
        else:
            self.request_count[now] += 1

    def get_coins(self) -> list[Coin]:
        """
        https://docs.coingecko.com/v3.0.1/reference/coins-list
        :return:
        """
        api = "/coins/list/"
        r = self._request(api)
        response = json.loads(r.text)
        coins = [Coin(id_coingecko=c["id"], symbol=c["symbol"], name=c["name"]) for c in response]
        return coins

    def get_ohcl(self):
        """
        https://docs.coingecko.com/v3.0.1/reference/coins-id-ohlc
        :return:
        """

        api = "/coins/list/"
        r = self._request(api)
        return r.text

    def get_prices(self,
                   coins: list[Coin],
                   include_market_cap: bool = True,
                   include_24h_vol: bool = True,
                   include_24h_change: bool = True
                   ) -> list[Price]:
        """
        Get the current price for a list of coins
        https://docs.coingecko.com/v3.0.1/reference/simple-price
        :return:
        """
        coin_ids = [c.id_coingecko for c in coins]
        api = (f"/simple/price?vs_currencies={self.currency}"
               f"&ids={','.join(coin_ids)}"
               f"&include_market_cap={api_b(include_market_cap)}"
               f"&include_24h_vol={api_b(include_24h_vol)}"
               f"&include_24h_change={api_b(include_24h_change)}"
               f"&include_last_updated_at=true")
        r = self._request(api)
        response = json.loads(r.text)
        prices = []
        for coin in coins:
            c_info = response[coin.id_coingecko]
            time = datetime.fromtimestamp(float(c_info["last_updated_at"])/1000.0)
            prices.append(Price(
                coin_id=coin.id_coingecko,
                coin_symbol=coin.symbol,
                time=time,
                value=c_info[f"{self.currency}"],
                market_cap=c_info[f"{self.currency}_market_cap"],
                trading_vol_24h=c_info[f"{self.currency}_24h_vol"],
                value_change_24h=c_info[f"{self.currency}_24h_change"],
            ))
        return prices

    def get_coin_data(self,
                      id: str,
                      localization: bool = False,
                      tickers: bool = False,
                      market_data: bool = False,
                      community_data: bool = False,
                      developer_data: bool = False,
                      sparkline: bool = False,
                      ):
        """
        https://docs.coingecko.com/reference/coins-id
        :return:
        """

        api = "/coins/list/"
        r = self._request(api)
        return r.text