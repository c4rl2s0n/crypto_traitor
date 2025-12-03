import logging

from dependency_injector.wiring import inject, Provide

from traitor.core.agents.agent_base import AgentBase
from traitor.core.research.news.news_source import NewsSource
from traitor.core.services import NewsResearchService
from traitor.core.tools import NewsSummarAIzer, LLMAgent
from traitor.core.tools.ai import LLMGemini


class TradingAgent(AgentBase):
    name = "Trading"

    @inject
    def __init__(self, interval = Provide["config.intervals.TRADING"]):
        self.interval = interval
        self.llm = LLMGemini()
        logging.info(f"Init TradingAgent")

    def _do_task(self):
        logging.info("Do some trading...")
        try:
            poem = self.llm.process_text([
                "You are an extraordinary poet with deep love for money and capitalism!",
                "Write a short poem about how much money you have, how much you love money and how you are going to acquire more and more money!"
            ])
            print(f"[PurePoetry]\n{poem}")
        except Exception as e:
            logging.exception("Error while trading...")
