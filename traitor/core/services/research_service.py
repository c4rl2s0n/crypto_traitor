from traitor.core.research.journalist import Journalist
from traitor.core.research.news.news_source import NewsSource
from traitor.core.tools import NewsSummarAIzer


class ResearchService(object):

    def __init__(self):
        self.journalist = Journalist(summarizer=NewsSummarAIzer())

    def research_news(self, sources: list[NewsSource]):
        self.journalist.research_news(sources)
