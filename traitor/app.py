from traitor.config import container
from traitor.config.di_container import bootstrap
from traitor.data.repositories import *
from traitor.research.journalist import *
from traitor.research.market.coingecko import CoinGecko
from traitor.tools.ai.agents.llm_gemini import LLMGemini


def initialize_coins() -> list[Coin]:
    coin_repo = CoinRepository()
    if not coin_repo.empty():
        return coin_repo.get_all()

    # get list of available coins
    coin_gecko = CoinGecko()
    coins = coin_gecko.get_coins()
    coin_repo.add_all(coins)
    return coins


def activate_coin(coin: Coin):
    price_repo = PricesRepository()
    last_price = price_repo.last_price(coin.id)
    coin_gecko = CoinGecko()
    prices = coin_gecko.get_coin_historical_prices_precise(coin, t_from=last_price)
    price_repo.add_prices(prices)


def run():
    container.init_resources()
    container.wire(modules=[__name__])

    # TODO: Setup
    # TODO: Research Loop (News + Summarize)
    # TODO: Research Loop (Market + Analyze + Summarize)
    # TODO: Trading Loop
    initialize_coins()
    coin_repo = CoinRepository()
    coins = coin_repo.get_by_coingecko_ids(['bitcoin', 'zcash', 'monero'])
    for c in coins:
        activate_coin(c)


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

