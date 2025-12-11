import json

from dependency_injector.wiring import inject, Provide
from requests import Response

from traitor.core.data.models import Coin, ApiCoinID
from traitor.core.data.repositories import CoinRepository
from traitor.core.research.market.exchange_api import CryptoExchangeApi
from traitor.core.tools.api import urljoin
from traitor.core.tools.misc import dict_to_json


class StealthexApi(CryptoExchangeApi):

    name = "StealthEx"
    base_url = "https://api.stealthex.io/v4"

    ratelimit_count = 600

    apis = {
        "coins": "currencies",
        "exchange_rates": "rates/estimated-amount",
    }

    @inject
    def __init__(self, api_key: str = Provide["config.api_keys.STEALTHEX"]):
        self.api_key = api_key
        self.coin_repo = CoinRepository()

    def _get_request_headers(self, api: str | None = None) -> dict[str, str]:
        header = {
            "Authorization": f"Bearer {self.api_key}",
        }
        if api.startswith(self.apis["exchange_rates"]):
            header["Content-Type"] = "application/json"

        return header

    def _get_request_url(self, api: str) -> str:
        return urljoin(self.base_url, api)

    def _check_response_code(self, response: Response):
        pass

    def get_coins(self) -> list[Coin]:
        page_size = 250
        # TODO: maybe make network flexible in the future...
        api = f"currencies?network=mainnet&limit={page_size}"
        page = 0
        coins = set()
        while True:
            api_tmp = f"{api}&offset={page * page_size}"
            r = self._request(api_tmp)
            response = json.loads(r.text)
            if not isinstance(response, list) or len(response) == 0:
                break

            for coin in response:
                api_coin_id = coin["symbol"]
                api_coin_name = coin["name"]
                api_coin_network = coin["network"]

                # if the coin exists in the database, add the API reference to it
                db_coins = self.coin_repo.get_by_symbol_and_name(api_coin_id, api_coin_name)
                for db_coin in db_coins:
                    db_coin.apis.append(ApiCoinID(
                        coin_id=db_coin.id,
                        api_coin_id=api_coin_id,
                        api_name=self.name,
                    ))
                    coins.add(db_coin)
                self.coin_repo.update_all(db_coins)

            if len(response) < page_size:
                break

        return list(coins)


    def _get_exchange_rate(self, out_id: str, in_id: str, fixed: bool) -> float | None:
        api = self.apis["exchange_rates"]

        post_data = {
            "route": {
                "from": {
                    "symbol": out_id,
                    "network": "mainnet"
                },
                "to": {
                    "symbol": in_id,
                    "network": "mainnet"
                }
            },
            "estimation": "direct",
            "rate": "fixed" if fixed else "floating",
            "amount": 1,
        }
        r = self._request_post(api, dict_to_json(post_data))
        if r.status_code != 200:
            return None
        response = json.loads(r.text)
        return response["estimated_amount"]

