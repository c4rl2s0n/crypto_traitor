from datetime import datetime
import pandas as pd
from dependency_injector.wiring import inject, Provide

from sqlalchemy import text

from traitor.core.config import DBViews
from traitor.core.data.db import Database
from traitor.core.data.models import Price, PriceFeature
from traitor.core.data.repositories.repository import Repository


class PricesRepository(Repository):

    def __init__(self):
        super().__init__(model=Price)

    def get_last_price_date(self, coin_id: str) -> datetime | None:
        """
        returns the timestamp of the last stored price for a coin. None if no price exists for the given coin
        :param coin_id:
        :return:
        """
        query = (f"SELECT MAX(time) "
                 f"FROM prices "
                 f"WHERE coin_id = :id")
        parameters = {"id": coin_id}
        with self.db.engine.begin() as conn:
            result = conn.execute(text(query), parameters)
            row = result.fetchone()  # returns a Row object or None
            if row:
                return row[0]  # first column
            return None

    def add_prices(self, prices: list[Price]):
        if len(prices) == 0:
            return
        with self.db.engine.begin() as conn:
            conn.execute(
                text("""INSERT INTO prices(coin_id, coin_symbol, time, value, market_cap, trading_vol_24h, value_change_24h) 
                        VALUES (:coin_id, :coin_symbol, :time, :value, :market_cap, :trading_vol, :value_change)
                        ON CONFLICT DO NOTHING;"""),
                [{
                    "coin_id": price.coin_id,
                    "coin_symbol": price.coin_symbol,
                    "time": price.time.isoformat(),
                    "value": price.value,
                    "market_cap": price.market_cap,
                    "trading_vol": price.trading_vol_24h,
                    "value_change": price.value_change_24h
                } for price in prices]
            )

    def _get_prices_query(self, coin_ids: list[str], start: datetime | None = None, end: datetime | None = None) -> (str, dict[str, str | list[str]]):
        query = (f"SELECT coin_id, coin_symbol, time, value, market_cap, trading_vol_24h, value_change_24h "
                 f"FROM prices "
                 f"WHERE coin_id = ANY(:ids)")
        parameters: dict[str, str | list[str]] = {"ids": coin_ids}
        if start is not None:
            query += f" {'AND time >= :start' if start is not None else ''} "
            parameters["start"] = start.isoformat()
        if end is not None:
            query += f" {'AND time <= :end' if end is not None else ''} "
            parameters["end"] = end.isoformat()
        return query, parameters

    def _get_prices_daily_ohlc_query(self, coin_id: str, start: datetime | None = None, end: datetime | None = None) -> (str, dict[str]):
        query = (f"SELECT coin_id, coin_symbol, day, open, high, low, close "
                 f"FROM {DBViews.daily_ohlc} "
                 f"WHERE coin_id = :id")
        parameters = {"id": coin_id}
        if start is not None:
            query += f" {'AND day >= :start' if start is not None else ''} "
            parameters["start"] = start.isoformat()
        if end is not None:
            query += f" {'AND day <= :end' if end is not None else ''} "
            parameters["end"] = end.isoformat()
        return query, parameters

    def get_prices_dict(self, coin_ids: list[str], start: datetime | None = None, end: datetime | None = None) -> list[dict]:
        query, parameters = self._get_prices_query(coin_ids, start, end)
        with self.db.engine.begin() as conn:
            result = conn.execute(text(query), parameters)
            # TODO: turn results into dict
            return [dict(row) for row in result.mappings()]

    def get_prices_df(self, coin_ids: list[str], start: datetime | None = None, end: datetime | None = None) -> pd.DataFrame:
        query, parameters = self._get_prices_query(coin_ids, start, end)
        with self.db.engine.begin() as conn:
            df = pd.read_sql(
                text(query),
                conn,
                params=parameters
            )
            return df

    def get_prices_daily_ohlc_df(self, coin_id: str, start: datetime | None = None, end: datetime | None = None) -> pd.DataFrame:
        query, parameters = self._get_prices_daily_ohlc_query(coin_id, start, end)
        with self.db.engine.begin() as conn:
            df = pd.read_sql(
                text(query),
                conn,
                params=parameters
            )
            return df
