import logging

from dateutil.relativedelta import relativedelta
from dependency_injector.wiring import inject, Provide

from traitor.core.agents.agent_base import AgentBase
from traitor.core.config import PROMPTS
from traitor.core.research.news.news_source import NewsSource
from traitor.core.services import NewsResearchService
from traitor.core.tools import NewsSummarAIzer, LLMAgent


class NewsResearchAgent(AgentBase):
    name = "News Research"

    @inject
    def __init__(self, sources: list[NewsSource] = Provide["news_sources"], interval: relativedelta = Provide["config.intervals.NEWS"]):
        self.interval = interval
        self.sources = sources
        self.research_service = NewsResearchService(summarizer=NewsSummarAIzer())
        logging.info(f"Init Agent {self.name}\n\tLLM: {self.research_service.summarizer.model}\n\tSources: {[s.name for s in sources]}")

    def _do_task(self):
        logging.info("Update news...")
        try:
            self.research_service.research_news(self.sources)
        except Exception as e:
            logging.exception("Error while researching...")
