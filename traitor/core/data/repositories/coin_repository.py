import logging
from typing import List

from sqlalchemy import select, and_, update
from sqlalchemy.orm import selectinload, Session

from traitor.core.data.models import ApiCoinID, CoinUrl
from traitor.core.data.models.coin import Coin
from traitor.core.data.repositories.repository import Repository


class CoinRepository(Repository):
    def __init__(self):
        super().__init__(model=Coin)

    def update_urls(self, urls: list[CoinUrl]):
        with self.db.write_session() as s:
            [s.merge(url) for url in urls]

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

    def get_by_ids(self, ids: list[int]) -> list[Coin]:
        with self.db.read_session() as s:
            return (s.query(Coin)
                .filter(Coin.id.in_(ids))
                .all())

    def try_get(self, input_value: str, active_only: bool = False) -> Coin | None:
        coin = self.get_by_symbols([input_value.lower()], active_only)
        if coin is None or len(coin) == 0:
            coin = self.get_by_names([input_value], active_only)
        if coin is None or len(coin) == 0:
            return None
        if len(coin) > 1:
            logging.warn(f"Found {len(coin)} coins for the input '{input_value}'")
        return coin[0]

    def get_by_symbols(self, symbols: list[str], active_only: bool = False) -> list[Coin]:
        with self.db.read_session() as s:
            q= (s.query(Coin)
                    .options(selectinload(Coin.apis))
                .join(Coin.apis)
                .filter(Coin.symbol.in_(symbols)))
            if active_only:
                q.filter(Coin.active == True)
            return q.all()

    def get_by_names(self, names: list[str], active_only: bool = False) -> list[Coin]:
        with self.db.read_session() as s:
            q =  (s.query(Coin)
                    .options(selectinload(Coin.apis))
                .join(Coin.apis)
                .filter(Coin.name.in_(names)))
            if active_only:
                q.filter(Coin.active == True)
            return q.all()

    def get_by_symbol_and_name(self, symbol: str, name: str) -> list[Coin]:
        with self.db.read_session() as s:
            return (s.query(Coin)
                    .options(selectinload(Coin.apis))
                .join(Coin.apis)
                .filter(
                    and_(
                        Coin.name == name,
                        Coin.symbol == symbol,
                    ))
                .all())

    def get_active(self) -> List[Coin]:
        with self.db.read_session() as s:
            return s.query(Coin).options(selectinload(Coin.apis)).filter(Coin.active).all()

    def clear_balance(self):
        with self.db.write_session() as s:
            s.execute(update(Coin).values(balance=0))

    def _trade_all(self):
        with self.db.write_session() as s:
            s.execute(update(Coin).values(can_trade=True))
