from typing import List

from sqlalchemy import or_

from data.db import Database
from data.models.coin import Coin


class CoinRepository(object):
    def __init__(self, db: Database):
        self.db = db

    def add(self, coin: Coin):
        self.db.session.add(coin)
        self.db.session.commit()

    def add_all(self, coins: List[Coin]):
        self.db.session.add_all(coins)
        self.db.session.commit()

    def get_active(self) -> List[Coin]:
        return self.db.session.query(Coin).filter(Coin.active).all()

    def commit(self):
        self.db.session.commit()
