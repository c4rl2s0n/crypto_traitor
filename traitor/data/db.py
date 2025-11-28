from sqlalchemy import create_engine, Index, text
from sqlalchemy.orm import declarative_base, sessionmaker

from traitor.data import Base
from traitor.data.models import *


class Database(object):
    def __init__(self, path: str):
        self.engine = create_engine(path, echo=True)

    def __enter__(self):
        print(f"Database connecting to {self.engine.url}")
        self._prepare_database()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session = self.SessionLocal()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing Database")
        self.close()

    def _prepare_database(self):
        # important for SQLAlchemy to correctly register the models!
        ApiCoinID.setup_indices()

        # setup database schema
        # Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

        # Setup TimescaleDB and hypertables
        with self.engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb;"))
            conn.execute(text("SELECT create_hypertable('prices', 'time', if_not_exists => TRUE, migrate_data => TRUE);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_price_coin_id_time ON prices(coin_id, time DESC);"))

        with self.engine.connect() as conn:
            conn.execution_options(isolation_level="AUTOCOMMIT").execute(text(
                """CREATE MATERIALIZED VIEW IF NOT EXISTS daily_ohlc
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


    def close(self):
        self.session.close()
