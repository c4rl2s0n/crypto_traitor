from typing import List

from dependency_injector.wiring import inject, Provide
from sqlalchemy import  select

from traitor.core.data.db import Database
from traitor.core.data.models import ApiCoinID
from traitor.core.data.models.coin import Coin


class CoinRepository(object):
    @inject
    def __init__(self, db: Database = Provide["db"]):
        self.db = db

    def empty(self) -> bool:
        exists = select(self.db.session.query(Coin).exists())
        return not self.db.session.execute(exists).scalar()

    def add(self, coin: Coin):
        self.db.session.add(coin)
        self.db.session.commit()

    def add_all(self, coins: List[Coin]):
        self.db.session.add_all(coins)
        self.db.session.commit()

    def get_all(self) -> list[Coin]:
        return self.db.session.query(Coin).all()

    def get_by_coingecko_ids(self, ids: list[str]) -> list[Coin]:
        return (self.db.session
                .query(Coin)
                .join(Coin.apis)
                .filter(
                    Coin.apis.any(
                        ApiCoinID.api_coin_id.in_(ids)
                    ))
                .all())

    def get_active(self) -> List[Coin]:
        return self.db.session.query(Coin).filter(Coin.active).all()

    def commit(self):
        self.db.session.commit()
