import logging
from datetime import timedelta, datetime

from dependency_injector.wiring import inject, Provide

from traitor.core.agents.agent_base import AgentBase
from traitor.core.data.models import SummaryTimeframe, Coin
from traitor.core.data.repositories import CoinRepository, ArticleRepository
from traitor.core.tools.ai.llm_tools import CoinStateTool


class CoinSpottingAgent(AgentBase):
    name = "Coin Spotting"
    interval = timedelta(days=1)

    @inject
    def __init__(self, interval = Provide["config.intervals.ANALYSIS"], model = Provide["summarize_agent_market"], prompts = Provide["prompts"]):
        self.interval = interval
        self.llm = model
        self.prompts = prompts

        self.article_repo = ArticleRepository()
        self.coin_repo = CoinRepository()

        logging.info(f"Init CoinSpottingAgent")

    def _do_task(self):
        logging.info("Looking for new coins...")
        active_coins = self.coin_repo.get_active()
        try:
            self.spot_new_coins(active_coins, SummaryTimeframe.DAY)
        except Exception as e:
            logging.exception(f"Error while spotting new coins...")




    def spot_new_coins(self, active_coins: list[Coin], timeframe: SummaryTimeframe):
        logging.info(f"Looking for new coins over last {timeframe}...")
        days_back = timeframe.value
        start_date = datetime.today() - timedelta(days=days_back)

        try:
            with open(self.prompts.coin_spotting, "r") as f:
                template = f.read()
        except FileNotFoundError:
            logging.error(f"Prompt file not found: {self.prompts.summarize_news_summaries}")
            return

        articles = self.article_repo.get_in_range(start_date, summarized_only=True)

        if len(articles) == 0:
            logging.debug("No articles to analyze. Stop CoinSpotting for now...")
            return

        article_strs: list[str] = []
        for article in articles:
            s = f"Date: {article.date_published}\n"
            s += f"Title: {article.title}\n"
            if article.source is not None:
                s += f"Source: {article.source}\n"
            s += f"Category: {article.category}\n"
            s += f"URL: {article.url}\n"
            s += f"Summary:\n{article.summary}\n"
            article_strs.append(s)

        prompt = template.format(
            active_coins="\n".join([f"- {c.name} ({c.symbol})" for c in active_coins]),
            articles="\n---\n".join(article_strs),
        )

        response = self.llm.process_tooled(
            contents=[prompt],
            tools=[CoinStateTool()],
            usage_comment="Coin Spotting",
        )

        logging.info(f"Spotting new Coins: {response}")