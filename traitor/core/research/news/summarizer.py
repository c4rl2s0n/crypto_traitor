import datetime

from dependency_injector.wiring import inject, Provide

from traitor.core.config.config import PROMPTS
from traitor.core.data.models.article import Article
from traitor.core.tools.ai.llm_agent import LLMAgent


class NewsSummarAIzer(object):
    @inject
    def __init__(self, model: LLMAgent = Provide["summarize_agent"], prompts: PROMPTS = Provide["prompts"]):
        self.model = model
        self.prompts = prompts

    def summarize_article(self, article: Article) -> str:
        return self.model.process_text([
            open(self.prompts.crypto_hft_json, "r").read(),
            f"Current Date: {datetime.date.today()}",
            str(article)
        ])

