import logging
from datetime import timedelta, datetime

from dateutil.relativedelta import relativedelta

from traitor.core.agents.agent_base import AgentBase
from traitor.core.data.models import PriceFeatureInterval
from traitor.core.data.repositories import CoinRepository, PricesRepository, PriceFeatureRepository
from traitor.core.tools.math.ts_analysis import extract_price_features


class PriceFeatureExtractionAgent(AgentBase):
    name = "Price Feature Extraction"
    interval = timedelta(minutes=5)
    feature_interval: PriceFeatureInterval

    def __init__(self, feature_interval: PriceFeatureInterval, interval: relativedelta):
        self.interval = interval
        self.feature_interval = feature_interval

        self.coin_repo = CoinRepository()
        self.price_repo = PricesRepository()
        self.price_feature_repo = PriceFeatureRepository()
        self.coins = self.coin_repo.get_active()
        self.coin_ids = [c.id for c in self.coins]
        logging.info(f"Init Agent {self.name}.\n\tFeature Interval: {self.feature_interval}\n\tActive coins: {self.coins}")

    @property
    def start(self) -> datetime | None:
        now = datetime.now()
        match self.feature_interval:
            case PriceFeatureInterval.ALL:
                return None
            case PriceFeatureInterval.YEAR:
                return (now - relativedelta(year=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            case PriceFeatureInterval.QUARTER:
                return (now - relativedelta(months=3)).replace(hour=0, minute=0, second=0, microsecond=0)
            case PriceFeatureInterval.MONTH:
                return (now - relativedelta(months=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            case PriceFeatureInterval.WEEK:
                return (now - relativedelta(weeks=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            case PriceFeatureInterval.DAY:
                return now - relativedelta(days=1)
            case PriceFeatureInterval.HOUR:
                return now - relativedelta(hours=1)

    def _do_task(self):
        # TODO: check if active coins have changed! This should be handled through an event to avoid unnecessary polling
        logging.info(f"Extracting price features (per {self.feature_interval})...")
        try:
            start = self.start

            # get the prices in the interval
            prices = self.price_repo.get_prices_df(self.coin_ids, start=start)

            # extract features for the prices
            features = extract_price_features(prices, interval=self.feature_interval)

            # update features in the database
            self.price_feature_repo.update_all(list(features.values()))
        except Exception as e:
            logging.exception("Error extracting price features")
