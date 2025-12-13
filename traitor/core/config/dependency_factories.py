from dateutil.relativedelta import relativedelta

from traitor.core.agents import AgentBase, TradingAgent, PriceWatchAgent,  NewsAnalysisAgent, NewsWatchAgent
from traitor.core.config import LLMProvider
from traitor.core.data.models import PriceFeatureInterval
from traitor.core.research.news import NewsSource
from traitor.core.research.news.sources import CoinDesk, CryptoSlate
from traitor.core.tools.ai import LLMGemini, LLMOpenAI


def agent_factory() -> list[AgentBase]:
    agents: list[AgentBase] = [
        TradingAgent(),
        PriceWatchAgent(),
        NewsWatchAgent(),
        NewsAnalysisAgent(),
    ]
    return agents

def price_feature_interval_factory() -> list[PriceFeatureInterval]:
    return [
        PriceFeatureInterval.ALL,
        PriceFeatureInterval.YEAR,
        PriceFeatureInterval.MONTH,
        PriceFeatureInterval.WEEK,
        PriceFeatureInterval.DAY,
    ]

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
