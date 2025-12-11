from .agent_base import AgentBase
from .coin_spotting_agent import CoinSpottingAgent
from .news_research_agent import NewsResearchAgent
from .price_analysis_agent import PriceAnalysisAgent
from .price_feature_extraction_agent import PriceFeatureExtractionAgent
from .price_watch_agent import PriceWatchAgent
from .trading_agent import TradingAgent
from .news_analysis_agent import NewsAnalysisAgent

__all__ = [
    # base
    "AgentBase",
    # options
    "CoinSpottingAgent",
    "NewsAnalysisAgent",
    "NewsResearchAgent",
    "PriceAnalysisAgent",
    "PriceFeatureExtractionAgent",
    "PriceWatchAgent",
    "TradingAgent",
]
