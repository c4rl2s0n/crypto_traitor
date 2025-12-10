import enum
import threading
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import requests
from requests import Response

from traitor.core.data.models import Coin, ApiCoinID, CoinApiType
from traitor.core.research.market.exceptions import ApiNotSupportedException



class CryptoApiBase(ABC):
    name: str
    currency = "usd"
    api_type: CoinApiType

    # ratelimit counter
    _lock = threading.Lock()
    # how many requests are allowed to the api (per window)
    ratelimit_count: int
    ratelimit_window: timedelta = timedelta(minutes=1)
    # True: fixed ratelimit window (bound to clock); False: sliding window (n requests in past n seconds)
    ratelimit_window_fixed: bool = True
    request_history: list[datetime] = []

    @abstractmethod
    def _get_request_headers(self, api: str | None = None) -> dict[str, str]:
        """
        generate the required headers to access an api
        :param api:
        :return:
        """
        pass

    @abstractmethod
    def _get_request_url(self, api: str) -> str:
        """
        generate the full URL for the given API endpoint
        :param api:
        :return:
        """
        pass

    def _request(self, api: str) -> Response:
        self._respect_ratelimit()

        headers = self._get_request_headers(api)
        self._count_request()
        response = requests.get(self._get_request_url(api), headers=headers, timeout=10)
        self._check_response_code(response)
        return response

    def _request_post(self, api: str, data: str | dict) -> Response:
        self._respect_ratelimit()

        headers = self._get_request_headers(api)
        self._count_request()
        response = requests.post(self._get_request_url(api), data=data, headers=headers, timeout=10)
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

    def _supported_coins(self, coins: list[Coin]) -> list[Coin]:
        """
        filters the given coins for supported ones
        :param coins:
        :return:
        """
        return [coin for coin in coins if coin.get_api(self.name) is not None]

    @abstractmethod
    def _check_response_code(self, response: Response):
        """
        Check the response code according to API docs
        :param response:
        :return:
        """
        pass

    @classmethod
    def _count_request(cls):
        """
        Count the number of api requests in the last minute
        :return:
        """
        now = datetime.now()
        if cls.ratelimit_window_fixed:
            now = now.replace(second=0, microsecond=0)

        with cls._lock:
            cls.request_history.append(now)

    @classmethod
    def _check_ratelimit(cls) -> timedelta:
        """
        check the API ratelimit and return the delay to wait before sending another request
        :return:
        """
        now = datetime.now()
        with cls._lock:
            window_start = now - cls.ratelimit_window
            history = [h for h in cls.request_history if h >= window_start]
            cls.request_history = history
            count = len(history)
            if count < cls.ratelimit_count or now - history[0] > cls.ratelimit_window:
                # no need to wait
                return timedelta()
            # wait for the minute of the
            return now - (history[0] + timedelta(minutes=1, seconds=1))

    @classmethod
    def _respect_ratelimit(cls):
        # check ratelimit and wait for the delay to continue requesting the api
        delay = cls._check_ratelimit()
        if delay.total_seconds() > 0:
            time.sleep(delay.total_seconds())

    @abstractmethod
    def get_coins(self) -> list[Coin]:
        """
        get a list of all coins that are supported by the API
        :return:
        """
        pass