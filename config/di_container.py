from dependency_injector import containers, providers

from config.config import *
from data.db import Database
from data.repositories import *


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    prompts = providers.Singleton(PROMPTS)

    db = providers.Singleton(Database, path=config.paths.DB)
    article_repository = providers.Singleton(ArticleRepository, db=db)
    coin_repository = providers.Singleton(CoinRepository, db=db)


# global container for dependency injection
container = Container()
