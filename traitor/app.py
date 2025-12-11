import logging
import threading
import time
from datetime import timedelta

from dateutil.relativedelta import relativedelta

import traitor
from traitor.core.agents import *
from traitor.core.agents.agent_base import stop_event
from traitor.core.agents.price_analysis_agent import PriceAnalysisAgent
from traitor.core.config import container, logs
from traitor.core.data.models import PriceFeatureInterval
from traitor.core.data.repositories import PriceFeatureRepository, ArticleRepository
from traitor.core.research.news import NewsSummarAIzer
from traitor.core.services import CoinService, NewsResearchService


# TODO: Setup:
#  - Load articles (if empty, or if some are missing a summary)
#  - Generate first news_summaries
#  -> Make sure LLM can start trading when all the agents are started
def setup():
    # delete all stored features to enforce re-analysis and avoid usage of outdated features
    price_feature_repo = PriceFeatureRepository()
    #price_feature_repo.clear()

    # scan for coins
    coin_service = CoinService()

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

    # make sure some articles are loaded before starting the bot
    article_repo = ArticleRepository()
    research_service = NewsResearchService(summarizer=NewsSummarAIzer())
    if article_repo.empty():
        # lookup news, if no articles are available
        research_service.research_news(container.news_sources())
    else:
        # otherwise, make sure all articles are summarized
        research_service.inspect_articles()



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
        traitor.core.tools.ai,
    ])

    # set up the bot
    setup()

    price_feature_extraction_agents = [
        PriceFeatureExtractionAgent(feature_interval=PriceFeatureInterval.ALL, interval=relativedelta(days=3)),
        PriceFeatureExtractionAgent(feature_interval=PriceFeatureInterval.YEAR, interval=relativedelta(days=1)),
        # PriceFeatureExtractionAgent(feature_interval=PriceFeatureInterval.QUARTER, interval=relativedelta(days=1)),
        PriceFeatureExtractionAgent(feature_interval=PriceFeatureInterval.MONTH, interval=relativedelta(hours=6)),
        PriceFeatureExtractionAgent(feature_interval=PriceFeatureInterval.WEEK, interval=relativedelta(hours=1)),
        PriceFeatureExtractionAgent(feature_interval=PriceFeatureInterval.DAY, interval=relativedelta(minutes=15)),
        # PriceFeatureExtractionAgent(feature_interval=PriceFeatureInterval.HOUR, interval=relativedelta(minutes=5)),
    ]
    agents: list[AgentBase] = [
        TradingAgent(),
        # PriceWatchAgent(),
        # NewsResearchAgent(),
        # PriceAnalysisAgent(interval=relativedelta(minutes=5)),
        # NewsAnalysisAgent(),
    ]
    # agents.extend(price_feature_extraction_agents)

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

