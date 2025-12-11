import logging
from contextlib import contextmanager
from typing import ContextManager

from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from traitor.core.config import DBViews
from traitor.core.data import Base
from traitor.core.data.models import *


class Database(object):
    def __init__(self, path: str):
        self.engine = create_engine(
                        path,
                        pool_size=5,
                        max_overflow=10,
                        pool_timeout=30,
                        pool_recycle=1800,
                        echo=False)

        print(f"Database connecting to {self.engine.url}")
        self._prepare_database()
        self.SessionFactory = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=self.engine)
        self.session = self.SessionFactory()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing Database")
        self.close()

    @contextmanager
    def read_session(self):
        session = self.SessionFactory()
        try:
            yield session
        except:
            session.rollback()
            raise
        finally:
            session.close()

    @contextmanager
    def write_session(self):
        session = self.SessionFactory()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def _prepare_database(self):
        ApiCoinID.setup_indices()

        # setup database schema
        # # Currently no migrations are implemented.
        # # When changing the database structure, uncomment drop_all to recreate the database
        # self._delete_database()
        Base.metadata.create_all(self.engine)

        # Setup TimescaleDB and hypertables
        with self.engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb;"))
            try:
                conn.execute(text("SELECT create_hypertable('prices', 'time', if_not_exists => TRUE, migrate_data => TRUE);"))
                conn.execute(text("SELECT create_hypertable('token_usage', 'time', if_not_exists => TRUE, migrate_data => TRUE);"))
            except Exception as e:
                logging.exception("failed to create hypertables")
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_price_coin_id_time ON prices(coin_id, time DESC);"))

        with self.engine.connect() as conn:
            conn.execution_options(isolation_level="AUTOCOMMIT").execute(text(
                f"""CREATE MATERIALIZED VIEW IF NOT EXISTS {DBViews.daily_ohlc}
                    WITH (timescaledb.continuous) AS
                    SELECT
                        coin_id,
                        coin_symbol,
                        time_bucket('1 day', "time") AS day,
                        FIRST("value", "time") AS open,
                        MAX("value") AS high,
                        MIN("value") AS low,
                        LAST("value", "time") AS close
                    FROM prices
                    GROUP BY coin_id, coin_symbol, time_bucket('1 day', "time");
                    """))

    def _delete_database(self):
        with self.engine.begin() as conn:
            conn.execute(text(f"DROP MATERIALIZED VIEW IF EXISTS {DBViews.daily_ohlc} CASCADE"))
            Base.metadata.drop_all(conn)


    def close(self):
        if hasattr(self, 'session') and self.session:
            self.session.close()
        self.engine.dispose(close=True)