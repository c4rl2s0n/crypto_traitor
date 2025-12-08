from typing import List

from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload, Session

from traitor.core.data.models import ApiCoinID
from traitor.core.data.models.coin import Coin
from traitor.core.data.repositories.repository import Repository


class CoinRepository(Repository):
    def __init__(self):
        super().__init__(model=Coin)

    def get_by_api_ids(self, api_name: str, ids: list[str]) -> list[Coin]:
        with self.db.read_session() as s:
            return (s.query(Coin)
                    .options(selectinload(Coin.apis))
                    .join(Coin.apis)
                    .filter(
                        Coin.apis.any(
                            and_(
                                ApiCoinID.api_name.is_(api_name),
                                ApiCoinID.api_coin_id.in_(ids),
                            )
                        ))
                    .all())

    def get_by_symbols(self, symbols: list[str]) -> list[Coin]:
        with self.db.read_session() as s:
            return (s.query(Coin)
                    .options(selectinload(Coin.apis))
                .join(Coin.apis)
                .filter(Coin.symbol.in_(symbols))
                .all())

    def get_by_names(self, names: list[str]) -> list[Coin]:
        with self.db.read_session() as s:
            return (s.query(Coin)
                    .options(selectinload(Coin.apis))
                .join(Coin.apis)
                .filter(Coin.name.in_(names))
                .all())

    def get_active(self) -> List[Coin]:
        with self.db.read_session() as s:
            return s.query(Coin).options(selectinload(Coin.apis)).filter(Coin.active).all()
