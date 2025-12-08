import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict

from traitor.core.data.models import Coin, CoinSummary
from traitor.core.data.repositories import AnalysisRepository
from traitor.core.tools import LLMAgent

class AnalysisService:
    def __init__(self, repository: AnalysisRepository, llm: LLMAgent):
        self.repository = repository
        self.llm = llm

    def analyze_coin(self, coin: Coin, timeframe_name: str, days_back: int):
        logging.info(f"Analyzing {coin.name} over last {timeframe_name}...")
        
        start_date = datetime.now() - timedelta(days=days_back)
        
        articles = self.repository.get_articles_in_range(start_date)
        
        relevant_data = []
        total_sentiment = 0.0
        count = 0

        for article in articles:
            try:
                raw_json = article.summary.replace("```json", "").replace("```", "").strip()
                data = json.loads(raw_json)
                
                assets = data.get("assets", [])
                for asset in assets:
                    ticker = asset.get("ticker") 
                    #logging.info(f"DEBUG : ASSET {ticker}")
                    #logging.info(f"DEBUG : COIN SYMBOL {coin.symbol}")
                    #logging.info(f"DEBUG : COIN NAME {coin.name.lower()}")
                    if asset.get("ticker").lower() == coin.symbol.lower() or coin.name.lower() in asset.get("ticker", "").lower():
                        
                        relevant_data.append(f"- [{article.date_published}] Sentiment {asset['sentiment']}: {asset.get('reasoning')} (Event: {data.get('event_type')})")
                        
                        total_sentiment += float(asset.get("sentiment", 0))
                        count += 1
                        
            except json.JSONDecodeError:
                logging.warning(f"Could not parse JSON for article {article.id}")
                continue

        if not relevant_data:
            logging.info(f"No relevant news found for {coin.name} in {timeframe_name}")
            return

        avg_sentiment = total_sentiment / count if count > 0 else 0

        prompt = self._create_analysis_prompt(coin.name, timeframe_name, avg_sentiment, relevant_data)
        meta_summary_text = self.llm.process_text([prompt])

        summary_obj = CoinSummary(
            coin_id=coin.id,
            timeframe=timeframe_name,
            sentiment_score=avg_sentiment,
            content=meta_summary_text
        )
        self.repository.add(summary_obj)
        logging.info(f"Analysis saved for {coin.name}: Score {avg_sentiment}")

    def _create_analysis_prompt(self, coin_name: str, timeframe: str, score: float, data: List[str]) -> str:
        data_text = "\n".join(data)
        return f"""
        You are a Crypto Strategic Analyst.
        
        Subject: {coin_name}
        Timeframe: Last {timeframe}
        Computed Sentiment Score: {score:.2f} (Scale -1.0 to 1.0)
        
        Raw Intelligence Data:
        {data_text}
        
        Task:
        Write a concise strategic report (max 3 sentences).
        1. Explain WHY the sentiment is positive/negative based on the events.
        2. Highlight the most critical event driving this score.
        3. Do NOT mention "JSON" or "data", speak like a financial advisor.
        """