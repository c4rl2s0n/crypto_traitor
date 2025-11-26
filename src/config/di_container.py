from dependency_injector import containers, providers

from src.config.config import *
from src.data.db import Database
from src.data.repositories import *
from src.data.timeseries import InfluxDB, TimeSeriesRepository
from src.research.market.coingecko import CoinGecko


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    prompts = providers.Singleton(PROMPTS)

    # SQLite DB setup
    db = providers.Singleton(Database, path=config.paths.DB)
    article_repository = providers.Singleton(ArticleRepository, db=db)
    coin_repository = providers.Singleton(CoinRepository, db=db)

    # Influx DB setup
    timeseries_db = providers.Singleton(
        InfluxDB,
        url=config.influx.DB_URL,
        token=config.influx.TOKEN,
        org=config.influx.ORG
    )
    timeseries_repository = providers.Singleton(TimeSeriesRepository, db=timeseries_db)

    coin_gecko = providers.Singleton(CoinGecko, api_key=config.api_keys.COINGECKO)


# global container for dependency injection
container = Container()
