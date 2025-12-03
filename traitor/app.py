import logging
import threading
import time

import traitor
from traitor.core.agents import *
from traitor.core.agents.agent_base import stop_event
from traitor.core.config import container, logs
from traitor.core.research.market.apis import CoinGecko
from traitor.core.research.news.sources import CoinDesk
from traitor.core.research.news.sources.cryptoslate import CryptoSlate
from traitor.core.services import CoinService


def setup():
    coin_service = CoinService(CoinGecko())

    # populate database with available coins
    if not coin_service.coins_loaded():
        coin_service.load_all_coins(force=True)

    coins = coin_service.get_active_coins()
    if len(coins) == 0:
        coins = coin_service.get_coins_by_name(['Bitcoin', 'Zcash', 'Monero'])
        for c in coins:
            coin_service.activate_coin(c)
    for coin in coins:
        coin_service.load_price_history(coin)


def run():
    """
    This function starts the lifecycle of the bot including
    - proper initial setup
    - running the different 'agents' in separate threads
    :return:
    """
    logs.setup()

    # set up the DI container
    container.init_resources()
    container.wire(modules=[
        __name__,
        traitor.core.data.repositories,
        traitor.core.data.repositories.repository,
        traitor.core.agents,
        traitor.core.services,
        traitor.core.research,
        traitor.core.data,
        traitor.core.tools,
    ])

    # set up the bot
    setup()

    agents: list[AgentBase] = [
        NewsResearchAgent([
            CoinDesk(),
            CryptoSlate(),
        ]),
        PriceWatchAgent(CoinGecko()),
        TradingAgent(),
    ]
    # Create threads
    threads = [
        threading.Thread(target=agent.run,  name=agent.name) for agent in agents
    ]

    # Start threads
    for t in threads:
        t.start()

    try:
        while True:
            time.sleep(0.5)  # main thread idle
    except KeyboardInterrupt:
        logging.info("Stopping all threads...")
        stop_event.set()  # notify threads

    # Wait for all threads to finish
    for t in threads:
        t.join()

    logging.info("Agents are tamed!\nShutting down...")


    # TODO: Research Loop (News + Summarize)
    # TODO: Research Loop (Market + Analyze + Summarize)
    # TODO: Trading Loop

    container.shutdown_resources()

