import logging
from datetime import timedelta

from traitor.core.agents.agent_base import AgentBase
from traitor.core.data.repositories import CoinRepository
from traitor.core.research.market import CryptoApi
from traitor.core.services import CoinService


class PriceWatchAgent(AgentBase):
    name = "Price Watch"
    interval = timedelta(minutes=5)

    def __init__(self, crypto_api: CryptoApi):
        self.coin_repo = CoinRepository()
        self.coins = self.coin_repo.get_active()
        self.coin_service = CoinService(crypto_api=crypto_api)
        logging.info(f"Init PriceWatchAgent.\n\tAPI: {crypto_api.name}\n\tActive coins: {self.coins}")

    def _do_task(self):
        # TODO: check if active coins have changed! This should be handled through an event to avoid unnecessary polling
        logging.info("Update prices...")
        try:
            # fetch update for prices and update database
            self.coin_service.get_current_prices(self.coins)
        except Exception as e:
            logging.exception("Error fetching prices")
