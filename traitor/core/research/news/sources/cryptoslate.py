import requests
from datetime import datetime
from typing import List, Set
from bs4 import BeautifulSoup
from traitor.core.data.models import Article, NewsSourceCategory
from traitor.core.research.news.news_source import NewsSource


class CryptoSlate(NewsSource):
    name = "CryptoSlate"
    url_base = "https://cryptoslate.com"

    # to fool the traitor_ui (don't know if it's necessary)
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    def categories(self) -> List[NewsSourceCategory]:
        categories = [
            NewsSourceCategory("News", "/news/"),
            NewsSourceCategory("Analysis", "/analysis/"),
        ]
        for c in categories:
            c.url = self.url_base + c.url
        return categories

    def get_articles_for_category(self, category: NewsSourceCategory) -> Set[str]:
        print(f"DEBUG: Downloading URL: {category.url}")
        try:
            response = requests.get(category.url, headers=self.HEADERS, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            return self._parse_articles_in_category(category, soup)
        except Exception as e:
            print(f"ERROR: Exception connecting to {category.url}: {e}")
            return set()

    def _parse_articles_in_category(self, category: NewsSourceCategory, soup: BeautifulSoup) -> set[str]:
        links = set()

        # We look for all articles on the page
        articles = soup.find_all('article')
        print(f"DEBUG: Found {len(articles)} <article> blocks in {category.name}")

        for article in articles:
            a_tag = article.find('a')

            if a_tag and a_tag.get('href'):
                link = a_tag['href']

                # Normalize URL (add domain if missing)
                if not link.startswith('http'):
                    link = self.url_base + link

                # DASH RULE (because I was having categories instead of articles sometimes)
                # Remove trailing slash if exists to correctly get the last part
                # Example: "https://web.com/news/bitcoin/" -> "bitcoin"
                # Example: "https://web.com/news/bitcoin-price-analysis" -> "bitcoin-price-analysis"
                clean_link = link.rstrip('/')
                slug = clean_link.split('/')[-1]

                # If there are NO dashes in the last part, we assume it's a category/hub and skip it
                if '-' not in slug:
                    print(f"DEBUG: Discarded (no dashes): {slug}")
                    continue

                # If it passes the filter, we add it
                links.add(link)

        print(f"DEBUG: Valid URLs after filtering: {len(links)}")
        return links

    def get_article(self, url: str, category: str) -> Article:
        try:
            response = requests.get(url, headers=self.HEADERS, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # 1. Parse the content
            article = self._parse_article(soup)

            # Manually assign the missing URL and Category
            article.url = url
            article.category = category

            return article
        except Exception as e:
            print(f"ERROR parsing article {url}: {e}")
            # Return an empty article but WITH URL so it doesn't break, although ideally we should handle the error better
            return Article(url=url, category=category, title="Error", date_published=datetime.now().date(), content="")

    def _parse_article(self, soup: BeautifulSoup) -> Article:
        title_tag = soup.find('h1')
        title = title_tag.text.strip() if title_tag else "No Title"

        # Note: Here we do NOT pass the URL, we inject it in get_article
        return Article(
            title=title,
            date_published=self._get_date(soup),
            content=self._get_content(soup)
        )

    def _get_content(self, soup: BeautifulSoup) -> str:
        # CryptoSlate often changes class names.
        # use post-header (seems as all the articles have it)
        article_body = soup.find('div', class_='post-header')

        if article_body:
            # Extract all <p> paragraphs
            paragraphs = article_body.find_all("p")

            # Filter out empty or very short paragraphs (advertising noise)
            text_content = []
            for p in paragraphs:
                text = p.text.strip()
                if len(text) > 20:  # Ignore short phrases like "Share this"
                    text_content.append(text)

            return "\n\n".join(text_content)

        return ""

    def _get_date(self, soup: BeautifulSoup) -> datetime.date:
        meta_date = soup.find('meta', property='article:published_time')
        if meta_date:
            try:
                date_str = meta_date['content']
                return datetime.strptime(date_str.split('T')[0], "%Y-%m-%d").date()
            except:
                pass
        return datetime.now().date()