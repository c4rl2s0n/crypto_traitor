import json
from datetime import datetime, timedelta

from dependency_injector.wiring import Provide, inject
from requests import Response

from traitor.core.data.models import *
from traitor.core.research.market.crypto_info_api import CryptoInfoApi
from traitor.core.research.market.exceptions import *
from traitor.core.tools.api import api_bool, urljoin, strings_from_dict


class CoinGecko(CryptoInfoApi):

    name: str = "CoinGecko"
    base_url: str = "https://api.coingecko.com/api/v3/"

    ratelimit_count: int = 30
    ratelimit_window = timedelta(minutes=1)

    @inject
    def __init__(self, api_key: str = Provide["config.api_keys.COINGECKO"]):
        self.api_key = api_key

    def _get_request_headers(self, api: str | None = None) -> dict[str, str]:
        return {
            "x-cg-demo-api-key": self.api_key,
        }

    def _get_request_url(self, api: str) -> str:
        return urljoin(self.base_url, api)

    def _check_response_code(self, response: Response):
        """
        Check the response code according to https://docs.coingecko.com/docs/common-errors-rate-limit
        :param response:
        :return:
        """
        if response.status_code == 401:
            # access denied
            raise AccessDeniedException()
        elif response.status_code == 429:
            # too many requests; probably exceeded rate limit
            raise RateLimitException()
        elif response.status_code == 10002:
            # missing API key
            raise MissingApiKeyException()
        elif response.status_code == 10010 or response.status_code == 10011:
            # invalid API key
            raise BadApiKeyException()

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

    def get_current_prices(self, coins: list[Coin]) -> list[Price]:
        """
        Get the current price for a list of coins
        https://docs.coingecko.com/v3.0.1/reference/simple-price
        :return:
        """
        coins = self._supported_coins(coins)
        api_coin_ids = [c.get_api(self.name).api_coin_id for c in coins]
        api = (f"/simple/price?vs_currencies={self.currency}"
               f"&ids={','.join(api_coin_ids)}"
               f"&include_market_cap={api_bool(True)}"
               f"&include_24hr_vol={api_bool(True)}"
               f"&include_24hr_change={api_bool(True)}"
               f"&include_last_updated_at=true")
        r = self._request(api)
        response = json.loads(r.text)
        prices = []
        for coin in coins:
            api_coin_id = coin.get_api(self.name).api_coin_id
            c_info = response[api_coin_id]
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

    def get_coin_historical_prices(self,
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

        # -------------------
        if t_from is not None and t_from.tzinfo is not None:
            t_from = t_from.replace(tzinfo=None)
        if t_to is not None and t_to.tzinfo is not None:
            t_to = t_to.replace(tzinfo=None)
        # -------------------

        self._check_coin(coin)

        min_from = datetime.now() - timedelta(days=365)
        if t_from is None or t_from < min_from:
            t_from = min_from
        if t_to is None or t_to < t_from:
            t_to = datetime.now()

        tmp_to = t_to
        result: list[Price] = []
        while tmp_to > t_from:
            # obtain data in chunks of 89 days
            tmp_from = max(t_from, tmp_to - timedelta(days=89))
            result.extend(self._get_coin_historical_prices(coin, tmp_from, tmp_to))
            tmp_to = tmp_from
        return result

    def _get_coin_historical_prices(self,
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

        # -------------------
        if t_from is not None and t_from.tzinfo is not None:
            t_from = t_from.replace(tzinfo=None)
        if t_to is not None and t_to.tzinfo is not None:
            t_to = t_to.replace(tzinfo=None)
        # -------------------

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

    def update_coin_info(self, coin: Coin) -> tuple[Coin, list[CoinUrl]]:
        """
        https://docs.coingecko.com/v3.0.1/reference/coins-id?playground=open
        :param coin:
        :return: updated Coin
        """

        api_coin_id = self._check_coin(coin)

        api = (f"/coins/{api_coin_id.api_coin_id}?localization=false"
               f"&community_data={api_bool(False)}"
               f"&developer_data={api_bool(False)}")
        r = self._request(api)
        response = json.loads(r.text)

        # extract URLs
        urls: list[CoinUrl] = [CoinUrl(coin_id=coin.id, url=entry[1], description=entry[0])
                               for entry in strings_from_dict(response["links"]) if entry[1].startswith("http")]

        # extract generic info
        description = response["description"]["en"]
        image = response["image"]["large"]
        genesis_date = response["genesis_date"]
        block_time = response["block_time_in_minutes"]
        coin.description = description
        coin.image = image
        coin.genesis_date = datetime.strptime(genesis_date, "%Y-%m-%d").date() if genesis_date is not None else None
        coin.block_time = block_time
        coin.initialized = True

        return coin, urls
