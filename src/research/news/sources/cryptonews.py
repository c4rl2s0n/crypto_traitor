from typing import List

from bs4 import BeautifulSoup

from src.data.models import Article, NewsSourceCategory
from src.research.news.news_source import NewsSource


# NOTE: this website did not work without javascript
class Cryptonews(NewsSource):
    url_base = "https://cryptonews.com/"

    def categories(self) -> List[NewsSourceCategory]:
        return [
            NewsSourceCategory("Press Releases", "press-releases/"),
            NewsSourceCategory("Altcoin News", "news/altcoin-news/")
        ]

    def _parse_articles_in_category(self, category: NewsSourceCategory, soup: BeautifulSoup) -> List[str]:
        return [a["href"] for a in soup.find_all('a', class_='archive-template-latest-news')]

    def _parse_article(self, soup: BeautifulSoup) -> Article:
        pass