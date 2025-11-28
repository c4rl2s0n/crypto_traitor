import datetime

from traitor.config.config import PROMPTS
from traitor.data.models.article import Article
from traitor.tools.ai.llm_agent import LLMAgent


class NewsSummarAIzer(object):
    def __init__(self, model: LLMAgent, prompts: PROMPTS):
        self.model = model
        self.prompts = prompts

    def summarize_article(self, article: Article) -> str:
        return self.model.process_text([
            open(self.prompts.summarize_news, "r").read(),
            f"Current Date: {datetime.date.today()}",
            str(article)
        ])

