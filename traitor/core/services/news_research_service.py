import logging
from datetime import date

from dependency_injector.wiring import inject, Provide

from traitor.core.config import PROMPTS
from traitor.core.data.models import Article
from traitor.core.data.repositories import ArticleRepository
from traitor.core.research.news import NewsSource
from traitor.core.tools.ai import LLMAgent


class NewsResearchService(object):

    @inject
    def __init__(self, model: LLMAgent = Provide["summarize_agent_news"], prompts: PROMPTS = Provide["prompts"]):
        self.model = model
        self.prompts = prompts
        self.article_repository = ArticleRepository()

    def research_news(self, sources: list[NewsSource]) -> list[Article]:
        self.look_for_articles(sources)
        return self.inspect_articles()


    def _summarize_article(self, article: Article) -> str:
        return self.model.process_text([
                open(self.prompts.summarize_news, "r").read(),
                f"Current Date: {date.today()}",
                str(article)
            ],
            usage_comment="Summarize News",
        )

    def look_for_articles(self, sources: list[NewsSource]):
        """
        Check the sources and get all the unknown articles
        :param sources:
        :return:
        """
        for source in sources:
            logging.debug(f"Getting articles from {source.name}")
            for category in source.categories():
                logging.debug(f"Checking {category.name}")

                # gather article-urls for category
                try:
                    urls = [url for url in source.get_articles_for_category(category)
                            if not self.article_repository.url_exists(url)]
                except:
                    logging.exception("Failed to gather articles for category")
                    continue

                # extract the contents for the articles
                articles = []
                for url in urls:
                    try:
                        articles.append(source.get_article(url, category.name))
                    except:
                        logging.exception(f"Failed to gather article for url '{url}'")
                        continue
                self.article_repository.add_all(articles)

    def inspect_articles(self) -> list[Article]:
        """
        Summarize all the new articles with visual progress
        :return:
        """
        # print("DEBUG: Searching articles without summary in the DB...")
        # Get articles without summary
        articles = self.article_repository.get_without_summary()

        total = len(articles)
        logging.debug(f"DEBUG: Found {total} articles to summarize with AI.")

        summarized: list[Article] = []
        if total == 0:
            return []

        for index, article in enumerate(articles):
            # Print progress: [1/20] Summarizing: Title...
            logging.debug(f" >> [{index + 1}/{total}] Summarizing: {article.title[:50]}...")

            try:
                # If the content is empty, don't summarize with AI
                if not article.content or len(article.content) < 50:
                    logging.debug(f"    WARNING: The article '{article.title}' has no content. Skipping.")
                    continue

                article.summary = self._summarize_article(article)

                # We save each article individually, so if the program fails we don't lose all progress
                self.article_repository.update(article)
                summarized.append(article)

            except Exception as e:
                logging.exception(f"summarizing article {article.title}: {e}")
                # If the API fails we stop ?
                # break

        logging.debug("Summary process finished.")
        return summarized