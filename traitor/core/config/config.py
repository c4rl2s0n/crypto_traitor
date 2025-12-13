import enum

from dateutil.relativedelta import relativedelta

class LLMProvider(enum.Enum):
    GEMINI = "Gemini"
    OPENAI = "OpenAI"

llm_provider = LLMProvider.OPENAI

class PROMPTS:
    _summarize_news_early_and_bad = "traitor/core/assets/prompts/summarize_news.md"
    _crypto_analyst_tags = "traitor/core/assets/prompts/prompt_crypto_analyst_tags.md"
    _crypto_hft_json = "traitor/core/assets/prompts/prompt_crypto_hft_json.md"

    _price_analysis = "traitor/core/assets/prompts/price_analysis.md"
    _news_analysis = "traitor/core/assets/prompts/news_analysis.md"
    _coin_spotting = "traitor/core/assets/prompts/coin_spotting.md"
    _trading = "traitor/core/assets/prompts/trading.md"
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
    def coin_spotting(self):
        """
        Used by AnalysisService to find new interesting coins
        """
        return self._coin_spotting
    
    @property
    def asset_analysis(self):
        return self._asset_analysis

    @property
    def trading(self):
        return self._trading

    @property
    def combine_prices_news(self):
        """
        Used to summarize price features
        :return:
        """
        return self._combine_prices_news


class INTERVALS:
    price_watch = relativedelta(minutes=3)
    price_analysis = relativedelta(minutes=30)
    news = relativedelta(hours=1)
    trading = relativedelta(minutes=30)
    news_analysis = relativedelta(hours=1)
    coin_spotting = relativedelta(hours=1)

class DBViews:
    daily_ohlc = "daily_ohlc"
    token_usage_grouped = "token_usage_grouped"
