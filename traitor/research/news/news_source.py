from abc import ABC, abstractmethod
from typing import List

from bs4 import BeautifulSoup

from traitor.data.models import Article, NewsSourceCategory
from traitor.tools import scraper


class NewsSource(ABC):
    name: str
    url_base: str

    @abstractmethod
    def categories(self) -> List[NewsSourceCategory]:
        pass

    @abstractmethod
    def _parse_articles_in_category(self, category: NewsSourceCategory, soup: BeautifulSoup) -> set[str]:
        pass

    def get_articles(self) -> set[str]:
        urls = set()
        for c in self.categories():
            for url in self.get_articles_for_category(c):
                urls.add(url)
        return urls

    def get_articles_for_category(self, category: NewsSourceCategory) -> set[str]:
        return scraper.extract(category.url, lambda s: self._parse_articles_in_category(category, s))

    @abstractmethod
    def _parse_article(self, soup: BeautifulSoup) -> Article:
        pass

    def get_article(self, url: str, category: str) -> Article:
        article = scraper.extract(url, self._parse_article)
        article.url = url
        article.category = category
        return article

