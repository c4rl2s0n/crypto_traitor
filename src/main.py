from src.config.bootstrap import bootstrap
from src.config import container
from src.research.journalist import *
from src.tools.ai.agents.llm_gemini import LLMGemini

bootstrap()

db = container.db()

article_repo = container.article_repository()
coin_repo = container.coin_repository()
journalist = Journalist(article_repo, coin_repo, NewsSummarAIzer(LLMGemini(), container.prompts()))

# journalist.lookup_coins([CoinMarketCap()])
# journalist.research_news([CoinDesk()])

# lookup all the available coins from CoinGecko
coin_gecko = container.coin_gecko()
coins = coin_gecko.get_coins()
coin_repo.add_all(coins)


db.close()
