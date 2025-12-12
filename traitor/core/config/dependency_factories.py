import enum

from dateutil.relativedelta import relativedelta

from traitor.core.agents import AgentBase, PriceFeatureExtractionAgent, TradingAgent, CoinSpottingAgent, PriceWatchAgent, \
    NewsResearchAgent, PriceAnalysisAgent, NewsAnalysisAgent
from traitor.core.config import LLMProvider
from traitor.core.data.models import PriceFeatureInterval
from traitor.core.research.news import NewsSource
from traitor.core.research.news.sources import CoinDesk, CryptoSlate
from traitor.core.tools.ai import LLMGemini, LLMOpenAI


def agent_factory() -> list[AgentBase]:
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
        # CoinSpottingAgent(),
        # PriceWatchAgent(),
        # NewsResearchAgent(),
        # PriceAnalysisAgent(interval=relativedelta(minutes=3)),
        # NewsAnalysisAgent(),
    ]
    # agents.extend(price_feature_extraction_agents)
    return agents

def news_source_factory() -> list[NewsSource]:
    return [CoinDesk(), CryptoSlate()]

def llm_factory_summarize_news(provider: LLMProvider):
    match provider:
        case LLMProvider.GEMINI:
            return LLMGemini(model="gemini-2.5-flash-lite")
        case LLMProvider.OPENAI:
            return LLMOpenAI(model="gpt-5-nano")

def llm_factory_summarize_prices(provider: LLMProvider):
    match provider:
        case LLMProvider.GEMINI:
            return LLMGemini(model="gemini-2.5-flash")
        case LLMProvider.OPENAI:
            return LLMOpenAI(model="gpt-5-nano")

def llm_factory_summarize_market(provider: LLMProvider):
    match provider:
        case LLMProvider.GEMINI:
            return LLMGemini(model="gemini-2.5-flash")
        case LLMProvider.OPENAI:
            return LLMOpenAI(model="gpt-5-nano")

def llm_factory_trading(provider: LLMProvider):
    match provider:
        case LLMProvider.GEMINI:
            return LLMGemini(model="gemini-2.5")
        case LLMProvider.OPENAI:
            return LLMOpenAI(model="gpt-5-mini")
