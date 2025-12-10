import logging
import json
import random
from datetime import datetime

from dateutil.relativedelta import relativedelta
from dependency_injector.wiring import inject, Provide

from traitor.core.agents.agent_base import AgentBase
from traitor.core.data.models import Coin, SummaryTimeframe
from traitor.core.research.market.apis.stealthexchange import StealthexApi
from traitor.core.research.news.news_source import NewsSource
from traitor.core.services import NewsResearchService
from traitor.core.tools import NewsSummarAIzer, LLMAgent
from traitor.core.data.repositories import CoinRepository, NewsAnalysisRepository, PriceAnalysisRepository, \
    TradingStrategyRepository, PricesRepository
from traitor.core.tools.ai import LLMGemini
from traitor.core.tools.ai.llm_tools import ExchangeRateTool, TradingStrategyTool
from traitor.core.tools.ai.llm_tools.trading import TradingTool
from traitor.core.tools.trading.paper_run import PaperRun
from traitor.core.tools.trading.wallet import Wallet


class TradingAgent(AgentBase):
    name = "Trading Desk"

    @inject
    def __init__(self, interval: relativedelta = Provide["config.intervals.TRADING"], model: LLMAgent = Provide["trading_agent"], prompts = Provide["prompts"]):
        self.interval = interval
        self.llm = model
        self.prompts = prompts

        self.coin_repo = CoinRepository()
        self.trading_strategy_repo = TradingStrategyRepository()
        self.news_repo = NewsAnalysisRepository()
        self.price_analysis_repo = PriceAnalysisRepository()
        self.price_repo = PricesRepository()
        self.coins = self.coin_repo.get_active()

        wallet = Wallet()
        for c in self.coins:
            wallet.register_coin(c)
            wallet.add(coin=c, amount=random.random())
        self.paper_run = PaperRun(initial_balance=wallet)

        logging.info(f"Init TradingAgent: Ready to merge intelligence.\n\t{wallet.portfolio_str()}")

    def _do_task(self):
        logging.info("Evaluating trading opportunities (News + Price)...")

        active_coins = self.coin_repo.get_active()

        # 4. Fusion of Intelligence (Decision Making)
        decision = self._make_strategic_decision(active_coins)

        logging.info(decision)


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
            with open(self.prompts.trading_strategy, "r") as f:
                template = f.read()
        except FileNotFoundError:
            logging.error(f"Critical: Prompt file not found at {self.prompts.trading_strategy}")
            return ""

        # 2. Fill the template
        prompt = template.format(
            coin_analysis="\n---\n".join(coin_analysis),
            date=datetime.now().strftime("%Y-%m-%d %H:%M"),
            trading_strategy=self._get_strategy()
        )
        logging.debug(f"Final Prompt:\n{prompt}")

        # 3. Query the LLM
        try:
            response_text = self.llm.process_tooled(
                contents=[prompt],
                tools=[
                    ExchangeRateTool(StealthexApi()),
                    TradingStrategyTool(),
                    TradingTool(self.paper_run)
                ]
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
            logging.error(f"Critical: Prompt file not found at {self.prompts.trading_strategy}")
            return None

        # 2. Fill the template
        prompt = template.format(
            coin_name=coin.name,
            coin_symbol=coin.symbol,
            coin_price=latest_price,
            coin_balance=self.paper_run.wallet.portfolio[coin.id],
            sentiment_score=news_summary.sentiment_score,
            news_summary=news_summary.content,
            # Assume price_data.analysis is the text/json of the technical analysis
            price_analysis=price_analysis.analysis
        )
        return prompt

    def _get_strategy(self) -> str:
        strategy = self.trading_strategy_repo.get_latest()
        if strategy is None:
            strategy = "No strategy yet. Define your strategy to perform consistent trading."
        return strategy