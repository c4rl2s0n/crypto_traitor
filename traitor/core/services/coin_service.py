from traitor.core.data.models import Coin
from traitor.core.data.repositories import CoinRepository, PricesRepository
from traitor.core.research.market.coingecko import CoinGecko


class CoinService(object):
    def __init__(self):
        self.coin_gecko = CoinGecko()
        self.coin_repo = CoinRepository()
        self.price_repo = PricesRepository()

    def load_all_coins(self) -> list[Coin]:
        if not self.coin_repo.empty():
            return self.coin_repo.get_all()

        # get list of available coins
        coin_gecko = CoinGecko()
        coins = coin_gecko.get_coins()
        self.coin_repo.add_all(coins)
        return coins

    def initialize_coin(self, coin: Coin) -> Coin:
        # initialize information about the coin
        if not coin.initialized:
            self.coin_gecko.update_coin_info(coin)

        # commit changes to database
        self.coin_repo.commit()
        return coin

    def activate_coin(self, coin: Coin) -> Coin:
        # update prices of the coin
        last_price_date = self.price_repo.get_last_price_date(coin.id)
        prices = self.coin_gecko.get_coin_historical_prices_precise(coin, t_from=last_price_date)
        self.price_repo.add_prices(prices)

        # initialize information about the coin
        self.initialize_coin(coin)

        coin.active = True
        # commit changes to database
        self.coin_repo.commit()

        return coin
