from typing import List

from traitor.core.data.repositories import ArticleRepository
from traitor.core.research.news.news_source import NewsSource
from traitor.core.tools.ai.summarizer import NewsSummarAIzer


class Journalist(object):
    def __init__(self, summarizer: NewsSummarAIzer):
        self.article_repository = ArticleRepository()
        self.summarizer = summarizer

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
        Summarize all the new articles with visual progress
        :return:
        """
        print("DEBUG: Searching articles without summary in the DB...")
        # Get articles without summary
        articles = self.article_repository.get_without_summary()
        
        total = len(articles)
        print(f"DEBUG: Found {total} articles to summarize with AI.")

        if total == 0:
            return

        for index, article in enumerate(articles):
            # Print progress: [1/20] Summarizing: Title...
            print(f" >> [{index + 1}/{total}] Summarizing: {article.title[:50]}...")
            
            try:
                # If the content is empty, don't summarize with AI
                if not article.content or len(article.content) < 50:
                    print(f"    WARNING: The article '{article.title}' has no content. Skipping.")
                else:
                    article.summary = self.summarizer.summarize_article(article)
                
                # We save each article individually, so if the program fails we don't lose all progress
                self.article_repository.commit() 
                
            except Exception as e:
                print(f"    ERROR summarizing article {article.id}: {e}")
                # If the API fails we stop ? 
                # break 

        print("DEBUG: Summary process finished.")