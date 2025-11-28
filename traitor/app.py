from traitor.core.data.models import Coin
from traitor.core.data.repositories import CoinRepository, PricesRepository
from traitor.core.config import container
from traitor.core.research.market.coingecko import CoinGecko
from traitor.core.research.news.sources.cryptoslate import CryptoSlate
from traitor.core.services import CoinService, ResearchService


def run():
    container.init_resources()
    container.wire(modules=[__name__])

    # TODO: Setup
    # TODO: Research Loop (News + Summarize)
    # TODO: Research Loop (Market + Analyze + Summarize)
    # TODO: Trading Loop
    coin_service = CoinService()
    coin_service.load_all_coins()

    coin_repo = CoinRepository()
    coins = coin_repo.get_by_coingecko_ids(['bitcoin', 'zcash', 'monero'])
    for c in coins:
        coin_service.activate_coin(c)

    research_service = ResearchService()
    research_service.research_news([CryptoSlate()])

    # article_repo = container.article_repository()
    # coin_repo = container.coin_repository()
    # price_repo = container.price_repository()
    # journalist = Journalist(article_repo, coin_repo, NewsSummarAIzer(LLMGemini(), container.prompts()))
    #
    # # journalist.lookup_coins([CoinMarketCap()])
    # # journalist.research_news([CoinDesk()])
    # # journalist.research_news([CryptoSlate()])
    #
    # # lookup all the available coins from CoinGecko
    # coin_gecko = container.coin_gecko()
    # # coins = coin_gecko.get_coins()
    # # coin_repo.add_all(coins)
    #
    # coins = coin_repo.get_by_coingecko_id(['bitcoin', 'zcash', 'monero'])
    # # prices = coin_gecko.get_prices(coins=coins)
    # # price_repo.add_prices(prices)
    # pdict = price_repo.get_prices_dict(coins[0].id)
    # pdf = price_repo.get_prices_df(coins[0].id)

    container.shutdown_resources()

