from traitor.core.data.models import Coin, Price
from traitor.core.data.repositories import CoinRepository, PricesRepository
from traitor.core.research.market import CryptoApi
from traitor.core.research.market.apis.coingecko import CoinGecko


class CoinService(object):
    def __init__(self, crypto_api: CryptoApi):
        self.crypto_api = crypto_api
        self.coin_repo = CoinRepository()
        self.price_repo = PricesRepository()

    def coins_loaded(self) -> bool:
        return not self.coin_repo.empty()

    def load_all_coins(self, force: bool = False) -> list[Coin]:
        if not force and self.coins_loaded():
            return self.coin_repo.get_all()

        # get list of available coins
        coin_gecko = CoinGecko()
        coins = coin_gecko.get_coins()
        self.coin_repo.add_all(coins)
        return coins

    def get_active_coins(self) -> list[Coin]:
        return self.coin_repo.get_active()

    def get_coins_by_symbol(self, symbols: list[str]) -> list[Coin]:
        return self.coin_repo.get_by_symbols(symbols)

    def get_coins_by_name(self, names: list[str]) -> list[Coin]:
        return self.coin_repo.get_by_names(names)

    def get_coins_by_api_id(self, api_name: str, ids: list[str]) -> list[Coin]:
        return self.coin_repo.get_by_api_ids(api_name, ids)

    def initialize_coin(self, coin: Coin) -> Coin:
        # initialize information about the coin
        if not coin.initialized:
            self.crypto_api.update_coin_info(coin)

        # commit changes to database
        self.coin_repo.update(coin)
        return coin

    def load_price_history(self, coin: Coin) -> Coin:
        # update prices of the coin
        last_price_date = self.price_repo.get_last_price_date(coin.id)
        prices = self.crypto_api.get_coin_historical_prices(coin, t_from=last_price_date)
        self.price_repo.add_prices(prices)

        self.coin_repo.update(coin)
        return coin

    def get_current_prices(self, coins: list[Coin]) -> list[Price]:
        # load the current prices for the given coins
        prices = self.crypto_api.get_current_prices(coins)

        # update the database
        self.price_repo.add_prices(prices)
        return prices

    def activate_coin(self, coin: Coin) -> Coin:
        self.load_price_history(coin)

        # initialize information about the coin
        self.initialize_coin(coin)

        coin.active = True

        # commit changes to database
        self.coin_repo.update(coin)

        return coin
