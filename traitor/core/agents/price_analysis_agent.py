import logging
from datetime import timedelta, datetime

from dateutil.relativedelta import relativedelta
from dependency_injector.wiring import inject, Provide

from traitor.core.agents.agent_base import AgentBase
from traitor.core.data.models import PriceFeatureInterval, Coin, PriceFeature, PriceAnalysis
from traitor.core.data.repositories import CoinRepository, PriceFeatureRepository, PriceAnalysisRepository, \
    PricesRepository
from traitor.core.tools import LLMAgent, dict_to_json


def _features_to_json(features: dict[PriceFeatureInterval, PriceFeature]) -> str:
    # json_dict = {k.name: v.to_dict() for k, v in features.items()}
    json_dict = {}

    # skip intervals where the timeframe is double (e.g. ALL_TIME and YEAR)
    checked = []
    for i1 in PriceFeatureInterval:
        if i1 not in features.keys():
            continue
        double = False
        for i2 in PriceFeatureInterval:
            if i2 in checked or i2 not in features.keys() or i1 == i2:
                continue
            if (features[i1].start == features[i2].start
                    and features[i1].end == features[i2].end):
                double = True
                break
        checked.append(i1)
        if double:
            continue
        json_dict[i1.value[0]] = features[i1].to_dict()
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
        self.price_repo = PricesRepository()
        self.price_analysis_repo = PriceAnalysisRepository()
        self.price_feature_repo = PriceFeatureRepository()
        logging.info(f"Init Agent {self.name}.")


    def _do_task(self):
        logging.info("Analyzing prices...")

        coins = self.coin_repo.get_active()
        try:
            for coin in coins:
                coin_features = self.price_feature_repo.get_features(coin.id)
                if len(coin_features) == 0:
                    logging.debug(f"No features available for coin {coin.name}. Skipping analysis.")
                    continue
                prompt = self._prepare_prompt(coin, coin_features)
                response = self.model.process_text([prompt])
                analysis = PriceAnalysis(
                    coin_id=coin.id,
                    time=datetime.now(),
                    analysis=response
                )
                self.price_analysis_repo.update(analysis)
        except Exception as e:
            logging.exception("Error analyzing prices")


    def _prepare_prompt(self, coin: Coin, features: dict[PriceFeatureInterval, PriceFeature]) -> str:
        try:
            with open(self.prompts.summarize_prices, "r") as f:
                template = f.read()
        except FileNotFoundError:
            logging.error(f"Prompt file not found: {self.prompts.summarize_prices}")
            return ""

        features_json_str = _features_to_json(features)
        prices_1h = self.price_repo.get_prices_dict([coin.id], start=datetime.now() - timedelta(hours=1))
        prices_str = "Last Hour Prices:\n"
        if prices_1h:
            for p in prices_1h:
                t_str = p["time"].strftime("%H:%M")
                val = p["value"]
                prices_str += f"- {t_str}: {val}\n"
        else:
            prices_str += "No recent price data available.\n"

        full_data_block = (
            f"Asset: {coin.name}\n\n"
            f"--- Computed Features ---\n{features_json_str}\n\n"
            f"--- {prices_str}"
        )
        return template.replace("{price_features_json}", full_data_block)
