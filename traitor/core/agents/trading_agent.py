import logging
import json
from datetime import datetime

from dateutil.relativedelta import relativedelta
from dependency_injector.wiring import inject, Provide

from traitor.core.agents.agent_base import AgentBase
from traitor.core.research.news.news_source import NewsSource
from traitor.core.services import NewsResearchService
from traitor.core.tools import NewsSummarAIzer, LLMAgent
from traitor.core.data.repositories import CoinRepository, AnalysisRepository, PriceAnalysisRepository
from traitor.core.tools.ai import LLMGemini


class TradingAgent(AgentBase):
    name = "Trading Desk"

    @inject
    def __init__(self, interval: relativedelta = Provide["config.intervals.TRADING"], prompts = Provide["prompts"]):
        self.interval = interval
        self.prompts = prompts

        self.llm = LLMGemini()
        
        self.coin_repo = CoinRepository()
        self.news_repo = AnalysisRepository()       
        self.price_repo = PriceAnalysisRepository()
        
        logging.info(f"Init TradingAgent: Ready to merge intelligence.")

    def _do_task(self):
        logging.info("Evaluating trading opportunities (News + Price)...")
        
        active_coins = self.coin_repo.get_active()
        
        for coin in active_coins:
            try:
                # 1. Recuperate INTELLIGENCE OF NEWS (Last 24h)
                news_summary = self.news_repo.get_latest_for_coin(coin.id, timeframe="7d")
                
                # 2. Recuperate INTELLIGENCE OF PRICES (Latest technical analysis, 7d)
                price_analysis = self.price_repo.get_latest_for_coin(coin.id)
                
                # 3. Validate that we have both data
                if not news_summary:
                    logging.debug(f"Skipping {coin.name}: No Fundamental Analysis found.")
                    continue
                    
                if not price_analysis:
                    logging.debug(f"Skipping {coin.name}: No Technical Analysis found.")
                    continue

                # 4. Fusion of Intelligence (Decision Making)
                decision = self._make_strategic_decision(coin, news_summary, price_analysis)
                
                if decision:
                    self._log_decision(coin, decision)
                    # HERE WOULD GO THE REAL BUY ORDER
            
            except Exception as e:
                logging.exception(f"Error processing strategy for {coin.name}")

    def _make_strategic_decision(self, coin, news_data, price_data) -> dict:
        """
        Prepare the prompt, query the LLM, and clean the resulting JSON.
        """
        # 1. Load the prompt from file
        try:
            with open(self.prompts.trading_strategy, "r") as f:
                template = f.read()
        except FileNotFoundError:
            logging.error(f"Critical: Prompt file not found at {self.prompts.trading_strategy}")
            return None

        # 2. Fill the template
        prompt = template.format(
            coin_name=coin.name,
            date=datetime.now().strftime("%Y-%m-%d %H:%M"),
            sentiment_score=news_data.sentiment_score,
            news_summary=news_data.content,
            # Assume price_data.analysis is the text/json of the technical analysis
            price_analysis=price_data.analysis 
        )

        # 3. Query the LLM
        try:
            response_text = self.llm.process_text([prompt])
            
            # 4. Clean Markdown (Sometimes Gemini wraps the JSON in ```json ... ```)
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            
            return json.loads(clean_text)
            
        except json.JSONDecodeError:
            logging.error(f"Failed to parse JSON decision for {coin.name}. Raw response: {response_text[:50]}...")
            return None
        except Exception as e:
            logging.error(f"LLM Error during decision making: {e}")
            return None

    def _log_decision(self, coin, decision):
        """
        Display the decision in a nicely formatted way on the console
        """
        action = decision.get('action', 'UNKNOWN').upper()
        confidence = decision.get('confidence', 0.0)
        risk = decision.get('risk_level', 'UNKNOWN')
        reason = decision.get('reasoning', 'No reasoning provided')
        
        log_level = logging.INFO
        
        # Visually highlight if there is a real action
        if action in ['BUY', 'SELL']:
            msg = f"\n🚨 TRADING SIGNAL [{coin.symbol}]: {action} 🚨\n"
            msg += f"   Confidence: {confidence:.2f} | Risk: {risk}\n"
            msg += f"   Reason: {reason}\n"
        else:
            msg = f"Trading Decision [{coin.symbol}]: HOLD (Conf: {confidence:.2f}) - {reason}"
            log_level = logging.INFO
            
        logging.log(log_level, msg)
