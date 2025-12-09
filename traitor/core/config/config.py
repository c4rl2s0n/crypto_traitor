from dateutil.relativedelta import relativedelta


class PROMPTS:
    _summarize_news_early_and_bad = "traitor/core/assets/prompts/summarize_news.md"
    _crypto_analyst_tags = "traitor/core/assets/prompts/prompt_crypto_analyst_tags.md"
    _crypto_hft_json = "traitor/core/assets/prompts/prompt_crypto_hft_json.md"
    _price_analysis = "traitor/core/assets/prompts/price_analysis.md"
    _news_analysis = "traitor/core/assets/prompts/news_analysis.md"

    @property
    def summarize_news(self):
        """
        Used by the NewsSummarAIzer to summarize news articles
        :return:
        """
        return self._crypto_hft_json

    @property
    def summarize_prices(self):
        """
        Used by the PriceAnalysisAgent to summarize price features
        :return:
        """
        return self._price_analysis
    
    @property
    def summarize_news_summaries(self):
        """
        Used by AnalysisService to generate the meta-summary
        """
        return self._news_analysis

class INTERVALS:
    price_watch = relativedelta(minutes=5)
    news = relativedelta(hours=1)
    trading = relativedelta(hours=1)
    analysis=relativedelta(hours=1)

class DBViews:
    daily_ohlc = "daily_ohlc"
