import logging

from dateutil.relativedelta import relativedelta
from dependency_injector.wiring import inject, Provide

from traitor.core.agents.agent_base import AgentBase
from traitor.core.data.models import SummaryTimeframe
from traitor.core.research.news.news_source import NewsSource
from traitor.core.services import NewsResearchService, CoinSpottingService


class NewsWatchAgent(AgentBase):
    name = "News Watch"

    @inject
    def __init__(self, sources: list[NewsSource] = Provide["news_sources"], interval: relativedelta = Provide["config.intervals.NEWS_WATCH"]):
        self.interval = interval
        self.sources = sources
        self.research_service = NewsResearchService()
        self.coin_spotting_service = CoinSpottingService()
        logging.info(f"Init Agent {self.name}\n\tLLM: {self.research_service.model}\n\tSources: {[s.name for s in sources]}")

    def _do_task(self):
        logging.info("Looking for new news...")
        try:
            self.research_service.look_for_articles(self.sources)

            # TODO: move this to use batch API; Then, run coin_spotting and news_analysis after a batch completes
            self.research_service.inspect_articles()
            self.coin_spotting_service.spot_new_coins(timeframe=SummaryTimeframe.DAY)
        except Exception as e:
            logging.exception("Error while researching...")
