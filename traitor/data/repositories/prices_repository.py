from datetime import datetime
import pandas as pd
from dependency_injector.wiring import inject, Provide

from influxdb_client import InfluxDBClient, Point, WritePrecision
from sqlalchemy import text

from traitor.data.db import Database
from traitor.data.models import Price


class PricesRepository(object):

    @inject
    def __init__(self, db: Database = Provide["db"]):
        self.db = db

    def last_price(self, coin_id: str) -> datetime | None:
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

    def _get_prices_query(self, coin_id: str, start: datetime | None = None, end: datetime | None = None) -> (str, dict[str]):
        query = (f"SELECT coin_id, coin_symbol, time, value, market_cap, trading_vol_24h, value_change_24h "
                 f"FROM prices "
                 f"WHERE coin_id = :id")
        parameters = {"id": coin_id}
        if start is not None:
            query += f" {'AND time >= :start' if start is not None else ''} "
            parameters["start"] = start.isoformat()
        if end is not None:
            query += f" {'AND time <= :end' if end is not None else ''} "
            parameters["end"] = end.isoformat()
        return query, parameters

    def _get_prices_query(self, coin_id: str, start: datetime | None = None, end: datetime | None = None) -> (str, dict[str]):
        query = (f"SELECT coin_id, coin_symbol, time, value, market_cap, trading_vol_24h, value_change_24h "
                 f"FROM prices "
                 f"WHERE coin_id = :id")
        parameters = {"id": coin_id}
        if start is not None:
            query += f" {'AND time >= :start' if start is not None else ''} "
            parameters["start"] = start.isoformat()
        if end is not None:
            query += f" {'AND time <= :end' if end is not None else ''} "
            parameters["end"] = end.isoformat()
        return query, parameters

    def get_prices_dict(self, coin_id: str, start: datetime | None = None, end: datetime | None = None) -> list[dict]:
        query, parameters = self._get_prices_query(coin_id, start, end)
        with self.db.engine.begin() as conn:
            result = conn.execute(text(query), parameters)
            # TODO: turn results into dict
            return [dict(row) for row in result.mappings()]

    def get_prices_df(self, coin_id: str, start: datetime | None = None, end: datetime | None = None) -> pd.DataFrame:
        query, parameters = self._get_prices_query(coin_id, start, end)
        with self.db.engine.begin() as conn:
            df = pd.read_sql(
                text(query),
                conn,
                params=parameters
            )
            return df

    def _get_prices_ohlc_query(self, coin_id: str, start: datetime | None = None, end: datetime | None = None) -> (str, dict[str]):
        query = (f"SELECT coin_id, coin_symbol, time, value, market_cap, trading_vol_24h, value_change_24h "
                 f"FROM prices "
                 f"WHERE coin_id = :id")
        parameters = {"id": coin_id}
        if start is not None:
            query += f" {'AND time >= :start' if start is not None else ''} "
            parameters["start"] = start.isoformat()
        if end is not None:
            query += f" {'AND time <= :end' if end is not None else ''} "
            parameters["end"] = end.isoformat()
        return query, parameters

