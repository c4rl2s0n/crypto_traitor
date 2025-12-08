import logging
from datetime import timedelta

from dependency_injector.wiring import inject, Provide

from traitor.core.agents.agent_base import AgentBase
from traitor.core.data.repositories import CoinRepository, AnalysisRepository
from traitor.core.services.analysis_service import AnalysisService
from traitor.core.tools.ai import LLMGemini

class AnalysisAgent(AgentBase):
    name = "Market Analyst"
    interval = timedelta(hours=1) 

    @inject
    def __init__(self, interval = Provide["config.intervals.ANALYSIS"]):
        self.interval = interval
        self.coin_repo = CoinRepository()
        self.analysis_repo = AnalysisRepository()
        
        self.service = AnalysisService(self.analysis_repo, LLMGemini())
        
        logging.info(f"Init AnalysisAgent")

    def _do_task(self):
        logging.info("Running market analysis...")
        
        active_coins = self.coin_repo.get_active()
        
        for coin in active_coins:
            try:
                # 1. Daily analysis (24h)
                #self.service.analyze_coin(coin, "24h", days_back=1)
                
                # 2. Weekly analysis (7d) - Optional, consumes more tokens
                self.service.analyze_coin(coin, "7d", days_back=7)

                # 3. Monthly analysis (30d) - Optional, consumes more tokens
                #self.service.analyze_coin(coin, "30d", days_back=30)
                
            except Exception as e:
                logging.exception(f"Error analyzing {coin.name}")