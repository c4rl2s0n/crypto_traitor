import logging
from datetime import timedelta, datetime

from dateutil.relativedelta import relativedelta
from dependency_injector.wiring import inject, Provide

from traitor.core.agents.agent_base import AgentBase
from traitor.core.data.models import PriceFeatureInterval, Coin, PriceFeature, PriceAnalysis
from traitor.core.data.repositories import CoinRepository, PriceFeatureRepository, PriceAnalysisRepository
from traitor.core.tools import LLMAgent, dict_to_json


def _features_to_json(features: dict[PriceFeatureInterval, PriceFeature]) -> str:
    json_dict = {k.name: v.to_dict() for k, v in features.items()}
    return dict_to_json(json_dict)


class PriceAnalysisAgent(AgentBase):
    name = "Price Analysis"
    interval = timedelta(minutes=5)

    @inject
    def __init__(self, interval: relativedelta = Provide["config.intervals.PRICES"], model: LLMAgent = Provide["summarize_agent_prices"], prompts = Provide["prompts"]):
        self.interval = interval
        self.prompts = prompts
        self.model = model

        self.coin_repo = CoinRepository()
        self.price_analysis_repo = PriceAnalysisRepository()
        self.price_feature_repo = PriceFeatureRepository()
        self.coins = self.coin_repo.get_active()
        logging.info(f"Init Agent {self.name}.\n\tActive coins: {self.coins}")


    def _do_task(self):
        # TODO: check if active coins have changed! This should be handled through an event to avoid unnecessary polling
        logging.info("Analyzing prices...")
        try:
            for coin in self.coins:
                coin_features = self.price_feature_repo.get_features(coin.id)
                if len(coin_features) == 0:
                    logging.debug(f"No features available for coin {coin.name}. Skipping analysis.")
                    continue
                prompt = self._prepare_prompt(coin, coin_features)
                response = self.model.ask_for_json([prompt])
                analysis = PriceAnalysis(
                    coin_id=coin.id,
                    time=datetime.now(),
                    analysis=response
                )
                self.price_analysis_repo.update(analysis)
        except Exception as e:
            logging.exception("Error analyzing prices")


    def _prepare_prompt(self, coin: Coin, features: dict[PriceFeatureInterval, PriceFeature]) -> str:
        template = open(self.prompts.summarize_prices, "r").read()
        template += f"Asset: {coin.name}\n\n"
        template += f"Price Features:\n{_features_to_json(features)}\n"

        return template
