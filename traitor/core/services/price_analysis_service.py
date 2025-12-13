import logging
import threading
from datetime import timedelta, datetime

from dependency_injector.wiring import inject, Provide

from traitor.core.data.models import Coin, PriceAnalysis, PriceFeatureInterval, PriceFeature
from traitor.core.data.repositories import CoinRepository, PricesRepository, PriceAnalysisRepository, PriceFeatureRepository
from traitor.core.tools import dict_to_json
from traitor.core.tools.ai import LLMAgent


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


class PriceAnalysisService(object):

    @inject
    def __init__(self, model: LLMAgent = Provide["summarize_agent_prices"], prompts = Provide["prompts"]):
        self.prompts = prompts
        self.model = model

        self.coin_repo = CoinRepository()
        self.price_repo = PricesRepository()
        self.price_analysis_repo = PriceAnalysisRepository()
        self.price_feature_repo = PriceFeatureRepository()

    def analyze_prices(self, coins: list[Coin] = None):
        logging.info("Analyzing coin prices...")

        if coins is None:
            coins = self.coin_repo.get_active()

        threads = [
            threading.Thread(target=self.analyze_coin_prices, args=(coin,),  name=f"PriceFeatureExtraction {coin.name}") for coin in coins
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def analyze_coin_prices(self, coin: Coin):
        logging.info(f"Analyzing prices for coin: {coin.name}...")

        try:
            coin_features = self.price_feature_repo.get_features(coin.id)
            if len(coin_features) == 0:
                logging.debug(f"No features available for coin {coin.name}. Abort analysis.")
                return
            prompt = self._prepare_prompt(coin, coin_features)
            response = self.model.process_text(
                [prompt],
                usage_comment="Price Analysis",
            )
            analysis = PriceAnalysis(
                coin_id=coin.id,
                time=datetime.now(),
                analysis=response,
            )
            self.price_analysis_repo.update(analysis)
        except Exception as e:
            logging.exception("Error analyzing prices")


    def _prepare_prompt(self, coin: Coin, features: dict[PriceFeatureInterval, PriceFeature]) -> str:
        template = open(self.prompts.summarize_prices, "r").read()
        template += f"Asset: {coin.name}\n\n"
        template += f"Price Features:\n{_features_to_json(features)}\n"
        prices_1h = self.price_repo.get_prices_dict([coin.id], start=datetime.now() - timedelta(hours=1))
        template += "Market values in the last hour:\n"
        for price in prices_1h:
            template += f"- {price["time"].strftime("%Y-%m-%d %H:%M")}: {price["value"]}\n"

        return template
