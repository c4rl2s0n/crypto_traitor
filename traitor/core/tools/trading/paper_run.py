import logging
import random
from datetime import datetime

from traitor.core.data.models import Coin, TradingLog
from traitor.core.data.repositories import PricesRepository, TradingLogRepository
from traitor.core.tools.trading.wallet import Wallet


class PaperRun(object):
    def __init__(self):
        self.wallet = Wallet()
        for cid in self.wallet.portfolio.keys():
            self.wallet.add(cid, random.random())

        self.price_repo = PricesRepository()
        self.trading_log_repo = TradingLogRepository()
        self.value_history = [self.wallet.total_value()]
        self.trade_log: list[TradingLog] = []

    def trade(self, coin_out: Coin, coin_in: Coin, balance_out: float, balance_in: float, reason: str|None = None) -> bool:
        if not self.wallet.verify_trade(coin_out.id, coin_in.id, balance_out):
            logging.warn("Tried to perform invalid trade")
            return False
        coin_out_price = self.price_repo.get_last_price(coin_out.id)
        coin_in_price = self.price_repo.get_last_price(coin_in.id)

        _trade = TradingLog(
            time=datetime.now(),
            coin_out_id=coin_out.id,
            coin_out_name=coin_out.name,
            balance_out=coin_out.balance,
            coin_out_value=coin_out_price.value if coin_out_price is not None else None,
            coin_in_id=coin_in.id,
            coin_in_name=coin_in.name,
            balance_in=coin_in.balance,
            coin_in_value=coin_in_price.value if coin_in_price is not None else None,
            comment=reason,
        )
        self.trade_log.append(_trade)
        self.trading_log_repo.add(_trade)

        self.wallet.remove(coin_out, balance_out)
        self.wallet.add(coin_in, balance_in)
        logging.info(f"Trade performed.\nPortfolio: {self.wallet.portfolio_str()}\nTotal value of the wallet: {self.wallet.total_value()}")
        return True

    def trade_log_preview(self, length: int | None = None) -> list[str]:
        logs: list[str] = []
        length = length if length is not None else len(self.trade_log)
        for i in range(1,length+1, -1):
            idx = len(self.trade_log) - i
            if idx < 0:
                break
            log = self.trade_log[idx]
            logs.append(log.to_string())

        return logs