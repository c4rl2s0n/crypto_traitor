from bootstrap import bootstrap
from config.di_container import container
from research.coins.sources.coinmarketcap import CoinMarketCap
from research.journalist import *
from research.news.sources.coindesk import CoinDesk
from tools.ai.agents.llm_gemini import LLMGemini

bootstrap()

db = container.db()

article_repo = container.article_repository()
coin_repo = container.coin_repository()
journalist = Journalist(article_repo, coin_repo, NewsSummarAIzer(LLMGemini(), container.prompts()))

# journalist.lookup_coins([CoinMarketCap()])
journalist.research_news([CoinDesk()])

db.close()
