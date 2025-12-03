from datetime import timedelta


class PROMPTS:
    summarize_news = "traitor/core/assets/prompts/summarize_news.md"
    crypto_analyst_tags = "traitor/core/assets/prompts/prompt_crypto_analyst_tags.md"
    crypto_hft_json = "traitor/core/assets/prompts/prompt_crypto_hft_json.md"

class INTERVALS:
    prices = timedelta(minutes=5)
    news = timedelta(hours=1)
    trading = timedelta(hours=1)

class DBViews:
    daily_ohlc = "daily_ohlc"
