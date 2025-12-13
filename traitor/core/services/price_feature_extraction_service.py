import logging
import threading
from datetime import datetime

import pandas as pd
from dateutil.relativedelta import relativedelta

from traitor.core.data.models import Coin, PriceFeatureInterval
from traitor.core.data.repositories import CoinRepository, PricesRepository, PriceFeatureRepository
from traitor.core.tools.math import extract_price_features
from traitor.core.tools.math.ts_custom import *


def _df_windows(interval: PriceFeatureInterval, prices_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    end: datetime = prices_df['time'].max()
    start_short: datetime = end
    start_long: datetime = end
    match interval:
        case PriceFeatureInterval.ALL:
            start_short = (end - relativedelta(months=6)).replace(hour=0, minute=0, second=0, microsecond=0)
            start_long = (end - relativedelta(years=4)).replace(hour=0, minute=0, second=0, microsecond=0)
        case PriceFeatureInterval.YEAR:
            start_short = (end - relativedelta(months=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            start_long = (end - relativedelta(months=6)).replace(hour=0, minute=0, second=0, microsecond=0)
        case PriceFeatureInterval.QUARTER:
            start_short = (end - relativedelta(weeks=3)).replace(hour=0, minute=0, second=0, microsecond=0)
            start_long = (end - relativedelta(months=2)).replace(hour=0, minute=0, second=0, microsecond=0)
        case PriceFeatureInterval.MONTH:
            start_short = (end - relativedelta(weeks=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            start_long = (end - relativedelta(weeks=4)).replace(hour=0, minute=0, second=0, microsecond=0)
        case PriceFeatureInterval.WEEK:
            start_short = (end - relativedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            start_long = (end - relativedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        case PriceFeatureInterval.DAY:
            start_short = end - relativedelta(minutes=30)
            start_long = end - relativedelta(hours=4)
        case PriceFeatureInterval.HOUR:
            start_short = end - relativedelta(minutes=10)
            start_long = end - relativedelta(hours=1)

    return (prices_df[prices_df["time"].between(start_short, end)],
            prices_df[prices_df["time"].between(start_long, end)])


def _get_start_ts(interval: PriceFeatureInterval) -> datetime | None:
    now = datetime.now()
    match interval:
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


class PriceFeatureExtractionService(object):

    def __init__(self):
        self.coin_repo = CoinRepository()
        self.price_repo = PricesRepository()
        self.price_feature_repo = PriceFeatureRepository()

    def extract_all(self, intervals: list[PriceFeatureInterval], coins: list[Coin] = None):
        self.price_feature_repo.clear()

        threads = [
            threading.Thread(target=self.extract_features, args=(interval, coins),  name=f"PriceFeatureExtraction {interval.name}") for interval in intervals
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def extract_features(self, interval: PriceFeatureInterval, coins: list[Coin] = None):
        logging.info(f"Extracting price features (per {interval})...")
        if coins is None:
            coins = self.coin_repo.get_active()
        coin_ids = [c.id for c in coins]

        try:
            start = _get_start_ts(interval)

            # get the prices in the interval
            prices = self.price_repo.get_prices_df(coin_ids, start=start)
            prices = prices.sort_values(["coin_id", "time"]).reset_index(drop=True)

            # extract features for the prices
            statistical_features = extract_price_features(prices, interval=interval)
            for coin_id in statistical_features.keys():
                feature = statistical_features[coin_id]
                c_prices_df = prices[prices["coin_id"] == coin_id]
                c_prices_np = c_prices_df["value"].to_numpy()
                c_volume_np = c_prices_df["trading_vol_24h"].to_numpy()
                prices_short, prices_long = _df_windows(interval, c_prices_df)

                # extract additional features (not covered by tsfresh)
                feature.returns = returns(c_prices_np)
                feature.slope = slope(c_prices_np)
                feature.volatility_regime = volatility_regime(prices_short["value"].to_numpy(), prices_long["value"].to_numpy())
                feature.max_drawdown = max_drawdown(c_prices_np)
                c_distance_from_high_low = distance_from_high_low(c_prices_np)
                feature.distance_from_high = c_distance_from_high_low["pct_from_high"]
                feature.distance_from_low = c_distance_from_high_low["pct_from_low"]
                feature.volatility_trend = volatility_trend(c_prices_np)
                feature.volume_trend = volume_trend(prices_short["trading_vol_24h"].to_numpy(), prices_long["trading_vol_24h"].to_numpy())
                feature.avg_volume = avg_volume(c_volume_np)
                feature.min_volume = min_volume(c_volume_np)
                feature.max_volume = max_volume(c_volume_np)

            # update features in the database
            self.price_feature_repo.update_all(list(statistical_features.values()))
        except Exception as e:
            logging.exception("Error extracting price features")
