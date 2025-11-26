from datetime import datetime
from typing import List

from bs4 import BeautifulSoup

from data.models import Article, NewsSourceCategory
from research.news.news_source import NewsSource


# NOTE: this website might have stopped to work without javascript -.-
class CoinDesk(NewsSource):
    name = "CoinDesk"
    url_base = "https://coindesk.com"

    def categories(self) -> List[NewsSourceCategory]:
        categories = [
            NewsSourceCategory("Markets", "/markets"),
            NewsSourceCategory("Finance", "/business"),
            NewsSourceCategory("Tech", "/tech"),
            NewsSourceCategory("Policy", "/policy"),
        ]
        for c in categories:
            c.url = self.url_base + c.url
        return categories

    def _parse_articles_in_category(self, category: NewsSourceCategory, soup: BeautifulSoup) -> set[str]:
        start = category.url.replace(self.url_base, "")
        paths = [a["href"] for a in soup.find('section').find_all('a') if
                 a["href"].startswith(start)]
        for i in range(len(paths)):
            if not paths[i].startswith(self.url_base):
                paths[i] = self.url_base + paths[i]
        return set(paths)

    def _parse_article(self, soup: BeautifulSoup) -> Article:
        title = soup.find('h1').text
        return Article(title=title, date_published=self._get_date(soup), content=self._get_content(soup))

    def _get_content(self, soup: BeautifulSoup) -> str:
        tag = soup.find(attrs={"data-module-name": "article-body"})
        paragraphs = tag.find_all("p")
        return "\n\n".join([p.text for p in paragraphs])

    def _get_date(self, soup: BeautifulSoup) -> datetime.date:
        header = soup.find(attrs={"data-module-name": "article-header"})
        spans = header.find_all("span")
        try:
            span = spans[-1]
            s = span.text

            # Remove "Published " prefix
            s = s.replace("Published", "")

            # Handle "a.m." / "p.m." by replacing "." to match strptime format
            s = s.replace("a.m.", "AM").replace("p.m.", "PM").strip()

            dt = datetime.strptime(s, "%b %d, %Y, %I:%M %p")
            return dt.date()
        except :
            return datetime.now().date()
