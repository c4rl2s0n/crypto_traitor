import datetime

from dependency_injector.wiring import inject, Provide

from traitor.core.config.config import PROMPTS
from traitor.core.data.models.article import Article
from traitor.core.tools.ai.llm_agent import LLMAgent


class NewsSummarAIzer(object):
    @inject
    def __init__(self, model: LLMAgent = Provide["summarize_agent_news"], prompts: PROMPTS = Provide["prompts"]):
        self.model = model
        self.prompts = prompts

    def summarize_article(self, article: Article) -> str:
        return self.model.process_text([
            open(self.prompts.summarize_news, "r").read(),
            f"Current Date: {datetime.date.today()}",
            str(article)
        ])

    def summarize_article(self, article: Article) -> str:
        try:
            with open(self.prompts.summarize_news, "r") as f:
                template = f.read()
        except FileNotFoundError:
            return "Error: Prompt file not found."
        
        article_text = (
            f"Date: {article.date_published}\n"
            f"Title: {article.title}\n"
            f"Body:\n{article.content}"
        )
        
        final_prompt = template.format(content=article_text)

        return self.model.process_text([final_prompt])

