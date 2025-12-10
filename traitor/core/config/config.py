from dateutil.relativedelta import relativedelta


class PROMPTS:
    _summarize_news_early_and_bad = "traitor/core/assets/prompts/summarize_news.md"
    _crypto_analyst_tags = "traitor/core/assets/prompts/prompt_crypto_analyst_tags.md"
    _crypto_hft_json = "traitor/core/assets/prompts/prompt_crypto_hft_json.md"

    _price_analysis = "traitor/core/assets/prompts/price_analysis.md"
    _news_analysis = "traitor/core/assets/prompts/news_analysis.md"
    _trading_strategy = "traitor/core/assets/prompts/trading_strategy.md"
    _asset_analysis = "traitor/core/assets/prompts/asset_analysis.md"

    _news_aggregation = "traitor/core/assets/prompts/news_aggregation.md"
    _combine_prices_news = "traitor/core/assets/prompts/combine_prices_news.md"

    @property
    def summarize_news(self):
        """
        Used to summarize the content of news articles
        :return:
        """
        return self._crypto_hft_json

    @property
    def aggregate_news(self):
        """
        Used to summarize a set of news-summaries into an asset-specific summary
        :return:
        """
        return self._news_aggregation

    @property
    def summarize_prices(self):
        """
        Used to summarize price features
        :return:
        """
        return self._price_analysis
    
    @property
    def summarize_news_summaries(self):
        """
        Used by AnalysisService to generate the meta-summary
        """
        return self._news_analysis
    
    @property
    def asset_analysis(self):
        return self._asset_analysis

    @property
    def trading_strategy(self):
        return self._trading_strategy

    @property
    def combine_prices_news(self):
        """
        Used to summarize price features
        :return:
        """
        return self._combine_prices_news


class INTERVALS:
    price_watch = relativedelta(minutes=5)
    news = relativedelta(hours=1)
    trading = relativedelta(minutes=15)
    analysis=relativedelta(hours=1)

class DBViews:
    daily_ohlc = "daily_ohlc"
