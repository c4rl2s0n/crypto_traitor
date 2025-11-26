from typing import List

from src.data.models import Coin
from src.data.repositories import ArticleRepository, CoinRepository
from src.research.coins.coin_source import CoinSource
from src.research.news.news_source import NewsSource
from src.tools.ai.summarizer import NewsSummarAIzer


class Journalist(object):
    def __init__(self, article_repository: ArticleRepository, coin_repository: CoinRepository, summarizer: NewsSummarAIzer):
        self.article_repository = article_repository
        self.coin_repository = coin_repository
        self.summarizer = summarizer

    def lookup_coins(self, sources: List[CoinSource]):
        all_coins: dict[str, Coin] = {}
        for source in sources:
            print(f"Lookup coins from {source.name}")
            coins = source.get_coins()
            for c in coins:
                if c.tag in all_coins:
                    ac = all_coins[c.tag]
                    if not ac.active and c.active:
                        ac.active = True
                    continue
                all_coins[c.tag] = c
        self.coin_repository.add_all(list(all_coins.values()))

    def research_news(self, sources: List[NewsSource]):
        self._gather_articles(sources)
        self._inspect_articles()

    def _gather_articles(self, sources: List[NewsSource]):
        """
        Check the sources and get all the unknown articles
        :param sources:
        :return:
        """
        for journalist in sources:
            print(f"Getting articles from {journalist.name}")
            for category in journalist.categories():
                print(f"Checking {category.name}")
                urls = [url for url in journalist.get_articles_for_category(category)
                        if not self.article_repository.url_exists(url)]
                articles = [journalist.get_article(url, category.name) for url in urls]
                self.article_repository.add_all(articles)

    def _inspect_articles(self):
        """
        Summarize all the new articles
        :return:
        """
        articles = self.article_repository.get_without_summary()
        for article in articles:
            article.summary = self.summarizer.summarize_article(article)
        self.article_repository.commit()
