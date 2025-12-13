import logging
import random
import threading
import time

import traitor
from traitor.core.agents import *
from traitor.core.agents.agent_base import stop_event
from traitor.core.config import container, logs
from traitor.core.data.repositories import PriceFeatureRepository, CoinRepository
from traitor.core.services import CoinService
from traitor.core.tools.ai import LLMOpenAI
from traitor.core.tools.trading.wallet import Wallet


# TODO: Setup:
#  - Load articles (if empty, or if some are missing a summary)
#  - Generate first news_summaries
#  -> Make sure LLM can start trading when all the agents are started
#  -> For real trading, setup would clear and update all coin balances!
#  -> instead of loading all coins from CoinGecko, maybe it is better to load the coins from StealthEX and then fetch additional info from CoinGecko?
def setup():
    # delete all stored features to enforce re-analysis and avoid usage of outdated features
    price_feature_repo = PriceFeatureRepository()
    price_feature_repo.clear()
    _randomize_balance()

    # scan for coins
    coin_service = CoinService()

    # populate database with available coins
    if not coin_service.coins_loaded():
        coin_service.load_all_coins(force=True)

    coins = coin_service.get_coins_by_name(['Bitcoin', 'Zcash', 'Monero', 'Solana', 'XRP', 'Ethereum', 'Tether', 'BNB', 'TRON', 'Litecoin'])
    for c in coins:
        if not c.active:
            coin_service.activate_coin(c)

    coins = coin_service.get_active_coins()
    for coin in coins:
        coin_service.load_price_history(coin)

def _randomize_balance():
    coin_repo = CoinRepository()
    coin_repo.clear_balance()
    # TODO: load real balances on start!
    wallet = Wallet()
    for cid in wallet.portfolio.keys():
        wallet.add(cid, random.random())

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
        traitor.core.research.market.apis,
        traitor.core.data,
        traitor.core.tools,
        traitor.core.tools.ai,
        traitor.core.tools.ai.llm_tools,
    ])

    # llm = LLMOpenAI()
    # r = llm.process_text(["Say hello"])
    # if "failed" in r:
    #     raise Exception("FAILED TO CONNECT TO LLM! ABORT!")

    # set up the bot
    setup()

    agents: list[AgentBase] = container.agents()

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

    container.shutdown_resources()

