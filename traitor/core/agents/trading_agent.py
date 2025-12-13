import logging
from datetime import datetime, timedelta
from typing import TypedDict

from dateutil.relativedelta import relativedelta
from dependency_injector.wiring import inject, Provide

from traitor.core.agents.agent_base import AgentBase
from traitor.core.data.models import Coin, SummaryTimeframe, TradingStrategy
from traitor.core.research.market.apis.stealthexchange import StealthexApi
from traitor.core.services import PriceAnalysisService, PriceFeatureExtractionService
from traitor.core.tools.ai import LLMAgent
from traitor.core.tools import time_to_str
from traitor.core.data.repositories import CoinRepository, NewsAnalysisRepository, PriceAnalysisRepository, \
    TradingStrategyRepository, PricesRepository, TradingLogRepository
from traitor.core.tools.ai.llm_tools import ExchangeRateTool, TradingStrategyTool, CoinStateTool
from traitor.core.tools.ai.llm_tools.trading import TradingTool
from traitor.core.tools.trading.paper_run import PaperRun


class TradingAgent(AgentBase):
    name = "Trading Desk"
    initial_delay = timedelta(minutes=0)

    @inject
    def __init__(self,
                 interval: relativedelta = Provide["config.intervals.TRADING"],
                 model: LLMAgent = Provide["trading_agent"],
                 prompts = Provide["prompts"],
                 price_feature_intervals = Provide["price_feature_intervals"]):
        self.interval = interval
        self.llm = model
        self.prompts = prompts
        self.price_feature_intervals = price_feature_intervals

        self.coin_repo = CoinRepository()
        self.trading_strategy_repo = TradingStrategyRepository()
        self.trading_log_repo = TradingLogRepository()
        self.news_repo = NewsAnalysisRepository()
        self.price_analysis_repo = PriceAnalysisRepository()
        self.price_repo = PricesRepository()

        self.price_analysis_service = PriceAnalysisService()
        self.price_feature_extraction_service = PriceFeatureExtractionService()

        self.paper_run = PaperRun()

        logging.info(f"Init TradingAgent: Ready to merge intelligence.\n{self.paper_run.wallet.portfolio_str()}\nTotal value: {self.paper_run.wallet.total_value()}")

    def _do_task(self):
        logging.info("Evaluating trading opportunities (News + Price)...")

        active_coins = self.coin_repo.get_active()
        # update price information (concurrently)
        self.price_feature_extraction_service.extract_all(self.price_feature_intervals, active_coins)
        self.price_analysis_service.analyze_prices(active_coins)

        # Fusion of Intelligence (Decision Making)
        decision = self._make_strategic_decision(active_coins)

        logging.info(decision)
        n = 5
        logging.info(f"Last {n} Trades: {self.paper_run.trade_log_preview(n)}")


    def _make_strategic_decision(self, coins: list[Coin]) -> str:
        """
        Prepare the prompt, query the LLM, and clean the resulting JSON.
        """

        coin_analysis = [self._get_coin_analysis(coin) for coin in coins]
        coin_analysis = [a for a in coin_analysis if a is not None]
        if len(coin_analysis) == 0:
            return "There is no information to analyze"

        # 1. Load the prompt from file
        try:
            with open(self.prompts.trading, "r") as f:
                template = f.read()
        except FileNotFoundError:
            logging.error(f"Critical: Prompt file not found at {self.prompts.trading}")
            return ""

        # 2. Fill the template
        prompt = template.format(
            coin_analysis="\n---\n".join(coin_analysis),
            date=datetime.now().strftime("%Y-%m-%d %H:%M"),
            strategy_history=self._get_strategy_history(1),
            trading_history=self._get_trading_history(5),
        )
        logging.debug(f"Final Prompt:\n{prompt}")

        # 3. Query the LLM
        try:
            response_text = self.llm.process_tooled(
                contents=[prompt],
                tools=[
                    ExchangeRateTool(),
                    TradingStrategyTool(),
                    TradingTool(self.paper_run),
                    CoinStateTool()
                ],
                usage_comment="Trading",
            )

            return response_text

        except Exception as e:
            logging.error(f"LLM Error during decision making: {e}")
            return ""


    def _get_coin_analysis(self, coin: Coin) -> str | None:
        # 1. Recuperate INTELLIGENCE OF NEWS
        news_summary = self.news_repo.get_latest_for_coin(coin.id, timeframe=SummaryTimeframe.WEEK)

        # 2. Recuperate INTELLIGENCE OF PRICES
        price_analysis = self.price_analysis_repo.get_latest_for_coin(coin.id)

        latest_price = self.price_repo.get_last_price(coin.id)


        # 3. Validate that we have both data
        if not news_summary:
            # TODO: Maybe don't 'drop' coins without news. (e.g. Monero did not show up in news, but we might still give the prices to the LLM?)
            #  maybe it is also better to drop it and instead include a news source for that crypto first...
            logging.debug(f"Skipping {coin.name}: No News Analysis found.")
            return None

        if not price_analysis:
            logging.debug(f"Skipping {coin.name}: No Price Analysis found.")
            return None

        # 1. Load the prompt from file
        try:
            with open(self.prompts.asset_analysis, "r") as f:
                template = f.read()
        except FileNotFoundError:
            logging.error(f"Critical: Prompt file not found at {self.prompts.trading}")
            return None

        # 2. Fill the template
        prompt = template.format(
            coin_name=coin.name,
            coin_symbol=coin.symbol,
            coin_price=latest_price.value,
            coin_balance=coin.balance,
            sentiment_score=news_summary.sentiment_score,
            news_summary=news_summary.content,
            # Assume price_data.analysis is the text/json of the technical analysis
            price_analysis=price_analysis.analysis
        )
        return prompt

    def _get_history(self, length: int = 10) -> str:
        strategies = self.trading_strategy_repo.get_latest(length)[::-1]
        if len(strategies) == 0:
            strategies.append(TradingStrategy(strategy="No strategy yet. Define your strategy to perform consistent trading.", time=datetime.now()))
        trading_history = self.trading_log_repo.get_latest(length)[::-1]
        history: list[HistoryEntry] = []
        for s in strategies:
            history.append({"time": s.time, "type": "Trading Strategy", "content": s.to_string(with_time=False)})
        for t in trading_history:
            history.append({"time": t.time, "type": "Trade", "content": t.to_string(with_time=False)})

        history = sorted(history, key=lambda x: x["time"])[:length]
        if len(history) > length and "Strategy:" not in "".join([h["content"] for h in history]) and len(strategies) > 0:
            strategy = strategies[-1]
            history[0] = {"time": strategy.time, "type": "Trading Strategy", "content": strategy.to_string(with_time=False)}
        result = "\n".join([f"[{time_to_str(h["time"])}] {h["type"]}\n{h["content"]}" for h in history])
        if len(history) > length:
            result = "(...)\n" + result
        return result


    def _get_strategy_history(self, count: int = 1) -> str:
        strategies = self.trading_strategy_repo.get_latest(count)[::-1]
        if len(strategies) == 0:
            strategies.append(TradingStrategy(strategy="No strategy yet. Define your strategy to perform consistent trading.", time=datetime.now()))
        result = "\n".join([s.to_string() for s in strategies])
        if len(strategies) > count:
            result = f"(...)\n{result}"
        return result

    def _get_trading_history(self, count: int = 1) -> str:
        history = self.trading_log_repo.get_latest(count)[::-1]
        if len(history) == 0:
            return "No trades have been performed yet."
        result = "\n".join([h.to_string(with_comment=True) for h in history])
        if len(history) > count:
            result = f"(...)\n{result}"
        return result


class HistoryEntry(TypedDict):
    time: datetime
    type: str
    content: str