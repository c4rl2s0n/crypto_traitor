import json
import logging
from datetime import datetime, timedelta

from traitor.core.config.config import PROMPTS
from traitor.core.data.models import Coin, CoinNewsSummary, SummaryTimeframe
from traitor.core.data.repositories import NewsAnalysisRepository, ArticleRepository
from traitor.core.tools import LLMAgent


class NewsAnalysisService:
    def __init__(self, llm: LLMAgent, prompts: PROMPTS):
        self.news_analysis_repo = NewsAnalysisRepository()
        self.article_repo = ArticleRepository()
        self.llm = llm
        self.prompts = prompts

    def analyze_coin(self, coin: Coin, timeframe: SummaryTimeframe):
        logging.info(f"Analyzing {coin.name} over last {timeframe}...")
        days_back = timeframe.value
        start_date = datetime.now() - timedelta(days=days_back)
        
        articles = self.article_repo.get_in_range(start_date, summarized_only=True)
        
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
            logging.info(f"No relevant news found for {coin.name} in {timeframe}")
            return

        avg_sentiment = total_sentiment / count if count > 0 else 0

        try:
            with open(self.prompts.summarize_news_summaries, "r") as f:
                template = f.read()
        except FileNotFoundError:
            logging.error(f"Prompt file not found: {self.prompts.summarize_news_summaries}")
            return

        prompt = template.format(
            coin_name=coin.name,
            timeframe=timeframe,
            score=f"{avg_sentiment:.2f}", 
            data_text="\n".join(relevant_data)
        )
        
        meta_summary_text = self.llm.process_text([prompt])

        summary_obj = CoinNewsSummary(
            coin_id=coin.id,
            timeframe=timeframe,
            sentiment_score=avg_sentiment,
            content=meta_summary_text
        )
        self.news_analysis_repo.add(summary_obj)
        logging.info(f"Analysis saved for {coin.name}: Score {avg_sentiment}")
