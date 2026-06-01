import logging
from backend.models.report import ReportState
from backend.tools.news_tool import fetch_news_and_sentiment
from backend.agents.market_agent import log_agent_step

logger = logging.getLogger(__name__)

async def run_sentiment_agent(state: ReportState, emitter_callback=None) -> ReportState:
    """
    Sentiment Agent: Gathers public news headlines and analyzes market sentiment.
    Operates under an explicit Think-Decide-Act-Observe loop.
    """
    log_agent_step(state, "SentimentAgent", "THINK", f"Beginning sentiment analysis for portfolio: {', '.join(state.tickers)}", emitter_callback)
    
    for ticker in state.tickers:
        # 1. THINK
        log_agent_step(state, "SentimentAgent", "THINK", f"Evaluating public narrative for stock '{ticker}'. I need to evaluate the media sentiment shift.", emitter_callback)
        
        # 2. DECIDE
        log_agent_step(state, "SentimentAgent", "DECIDE", f"Determined that NewsAPI + VADER sentiment analysis tool is optimal to process public data for '{ticker}'.", emitter_callback)
        
        # 3. ACT
        log_agent_step(state, "SentimentAgent", "ACT", f"Invoking fetch_news_and_sentiment('{ticker}')...", emitter_callback)
        
        try:
            news_data = fetch_news_and_sentiment(ticker)
            
            # 4. OBSERVE
            observation_msg = f"Retrieved news for '{ticker}'. Average Sentiment: {news_data['sentiment_avg']:.2f} ({news_data['sentiment_label']}) based on {len(news_data['headlines'])} headlines."
            log_agent_step(state, "SentimentAgent", "OBSERVE", observation_msg, emitter_callback)
            
            # Store in state
            state.sentiment_data[ticker] = news_data
            
        except Exception as e:
            error_msg = f"Failed to acquire news sentiment for '{ticker}': {str(e)}"
            log_agent_step(state, "SentimentAgent", "OBSERVE", f"ERROR: {error_msg}", emitter_callback)
            state.sentiment_data[ticker] = {
                "headlines": [],
                "sentiment_avg": 0.0,
                "sentiment_label": "Neutral"
            }
            
        # 5. REPEAT / CONTINUE
        log_agent_step(state, "SentimentAgent", "REPEAT", f"Sentiment analysis for '{ticker}' completed. Checking next available target...", emitter_callback)

    log_agent_step(state, "SentimentAgent", "COMPLETE", "Sentiment analysis successfully finalized across all target assets.", emitter_callback)
    return state
