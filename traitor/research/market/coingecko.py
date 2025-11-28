import json
from datetime import datetime, timedelta

import requests
from dependency_injector.wiring import inject, Provide
from requests import Response

from traitor.data.models import Price, Coin, ApiCoinID
from traitor.tools import api_b, urljoin


class ApiNotSupportedException(Exception):
    pass


class CoinGecko(object):
    name: str = "CoinGecko"
    base_url: str = "https://api.coingecko.com/api/v3/"
    request_count: dict[datetime, int] = {}

    currency = "usd"

    @inject
    def __init__(self, api_key: str = Provide["config.api_keys.COINGECKO"]):
        self.api_key = api_key

    def _request(self, api: str) -> Response:
        headers = {
            "x-cg-demo-api-key": self.api_key,
        }
        self._count_request()
        response = requests.get(urljoin(self.base_url, api), headers=headers, timeout=10)
        self._check_response_code(response)
        return response

    def _check_coin(self, coin: Coin) -> ApiCoinID:
        """
        Check, if the given coin can be handled by the api
        :param coin:
        :return:
        """
        coin_api_id = coin.get_api(self.name)
        if coin_api_id is None:
            raise ApiNotSupportedException(f"{coin.name} not supported for {self.name}")
        return coin_api_id

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
        coins = [Coin(
                    symbol=c["symbol"],
                    name=c["name"],
                    apis=[ApiCoinID(api_name=self.name, api_coin_id=c["id"])]
                ) for c in response]
        return coins

    def get_coin_info(self, coin: Coin,
                      localization: bool = False,
                      tickers: bool = False,
                      market_data: bool = False,
                      community_data: bool = False,
                      developer_data: bool = False,
                      sparkline: bool = False,) -> Coin:
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

    def get_current_prices(self,
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
               f"&include_24hr_vol={api_b(include_24h_vol)}"
               f"&include_24hr_change={api_b(include_24h_change)}"
               f"&include_last_updated_at=true")
        r = self._request(api)
        response = json.loads(r.text)
        prices = []
        for coin in coins:
            c_info = response[coin.id_coingecko]
            time = datetime.fromtimestamp(float(c_info["last_updated_at"]))
            prices.append(Price(
                coin_id=coin.id,
                coin_symbol=coin.symbol,
                time=time,
                value=c_info[f"{self.currency}"],
                market_cap=c_info[f"{self.currency}_market_cap"],
                trading_vol_24h=c_info[f"{self.currency}_24h_vol"],
                value_change_24h=c_info[f"{self.currency}_24h_change"],
            ))
        return prices

    def get_coin_historical_prices_precise(self,
                                           coin: Coin,
                                           t_from: datetime = None,
                                           t_to: datetime = None
                                           ) -> list[Price]:
        """
        gets the data in 3-month blocks to obtain hourly accuracy
        https://docs.coingecko.com/v3.0.1/reference/coins-id-market-chart-range
        :param coin:
        :param t_from: Timestamp from when to start getting prices. If None -> Today - 365
        :param t_to:  Timestamp to when to get the prices. If None -> Today
        :return:
        """
        self._check_coin(coin)

        min_from = datetime.now() - timedelta(days=365)
        if t_from is None or t_from < min_from:
            t_from = min_from
        if t_to is None or t_to < t_from:
            t_to = datetime.now()
        t_delta = t_to - t_from
        if t_delta.days <= 90:
            # less than 90 days can be obtained directly
            return self.get_coin_historical_prices(coin, t_from, t_to)
        tmp_to = t_to
        result: list[Price] = []
        while tmp_to > t_from:
            tmp_from = max(t_from, tmp_to - timedelta(days=89)) # , hours=23, minutes=59))
            result.extend(self.get_coin_historical_prices(coin, tmp_from, tmp_to))
            tmp_to = tmp_from
        return result

    def get_coin_historical_prices(self,
                                   coin: Coin,
                                   t_from: datetime = None,
                                   t_to: datetime = None
                                   ) -> list[Price]:
        """
        https://docs.coingecko.com/v3.0.1/reference/coins-id-market-chart-range
        :param coin:
        :param t_from: Timestamp from when to start getting prices. If None -> Today - 365
        :param t_to:  Timestamp to when to get the prices. If None -> Today
        :return:
        """
        coin_api_id = self._check_coin(coin)

        min_from = datetime.now() - timedelta(days=365)
        if t_from is None or t_from < min_from:
            t_from = min_from
        if t_to is None or t_to < t_from:
            t_to = datetime.now()

        api = (f"/coins/{coin_api_id.api_coin_id}/market_chart/range?vs_currency=usd"
               f"&from={int(t_from.timestamp()*1000)}"
               f"&to={int(t_to.timestamp()*1000)}")
        r = self._request(api)
        response = json.loads(r.text)
        prices = response["prices"]
        market_caps = response["market_caps"]
        total_volumes = response["total_volumes"]
        assert len(prices) == len(market_caps) == len(total_volumes)
        result: list[Price] = []
        for i in range(len(prices)):
            time = datetime.fromtimestamp(prices[i][0]/1000)
            price = Price(
                coin_id=coin.id,
                coin_symbol=coin.symbol,
                time=time,
                value=prices[i][1],
                market_cap=market_caps[i][1],
                trading_vol_24h=total_volumes[i][1],
                value_change_24h=None,
            )
            result.append(price)
        return result

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