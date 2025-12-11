import logging
from datetime import timedelta

from dateutil.relativedelta import relativedelta
from dependency_injector.wiring import inject, Provide

from traitor.core.agents.agent_base import AgentBase
from traitor.core.data.repositories import CoinRepository
from traitor.core.research.market import CryptoInfoApi
from traitor.core.services import CoinService


class PriceWatchAgent(AgentBase):
    name = "Price Watch"
    interval = timedelta(minutes=5)

    @inject
    def __init__(self, crypto_info_api: CryptoInfoApi = Provide["crypto_info_api"], interval:relativedelta = Provide["config.intervals.PRICE_WATCH"]):
        self.interval = interval
        self.coin_repo = CoinRepository()
        self.coin_service = CoinService(crypto_info_api=crypto_info_api)
        logging.info(f"Init Agent {self.name}.\n\tAPI: {crypto_info_api.name}.")

    def _do_task(self):
        logging.info("Update prices...")

        try:
            # fetch update for prices and update database
            coins = self.coin_repo.get_active()
            self.coin_service.get_current_prices(coins)
        except Exception as e:
            logging.exception("Error fetching prices")
