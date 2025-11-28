import traitor.data.models
from traitor.config import container
from traitor.research.journalist import *
from traitor.research.news.sources.cryptoslate import CryptoSlate
from traitor.tools.ai.agents.llm_gemini import LLMGemini


tmp = traitor.data.models.ApiCoinID.__name__

traitor.app.run()
exit(0)

db = container.db()

article_repo = container.article_repository()
coin_repo = container.coin_repository()
price_repo = container.price_repository()
journalist = Journalist(article_repo, coin_repo, NewsSummarAIzer(LLMGemini(), container.prompts()))

# journalist.lookup_coins([CoinMarketCap()])
# journalist.research_news([CoinDesk()])
# journalist.research_news([CryptoSlate()])

# lookup all the available coins from CoinGecko
coin_gecko = container.coin_gecko()
# coins = coin_gecko.get_coins()
# coin_repo.add_all(coins)

coins = coin_repo.get_by_coingecko_id(['bitcoin', 'zcash', 'monero'])
# prices = coin_gecko.get_prices(coins=coins)
# price_repo.add_prices(prices)
pdict = price_repo.get_prices_dict(coins[0].id)
pdf = price_repo.get_prices_df(coins[0].id)

db.close()
