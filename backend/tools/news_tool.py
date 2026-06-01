import os
import logging
from typing import Dict, Any, List
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import httpx
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

analyzer = SentimentIntensityAnalyzer()

# Realistic and contextual mock headlines to fallback on when NewsAPI keys are missing or limits are hit
MOCK_NEWS = {
    "AAPL": [
        {"title": "Apple unveils groundbreaking AI integration at its developer conference, stocks reach all-time high.", "source": "Bloomberg"},
        {"title": "DOJ files antitrust lawsuit targeting Apple's ecosystem restrictions.", "source": "Wall Street Journal"},
        {"title": "Supply chain demands show robust iPhone production in Asian hubs.", "source": "Reuters"},
        {"title": "Apple's service revenue continues double-digit expansion, cushioning hardware volatility.", "source": "MarketWatch"},
        {"title": "Global smartphone demand shows cooling trend, challenging near-term revenue targets.", "source": "TechCrunch"}
    ],
    "MSFT": [
        {"title": "Microsoft Copilot subscription revenue exceeds analyst forecasts by 15%.", "source": "TechCrunch"},
        {"title": "Azure cloud services grow 31% YoY, narrowing the gap with AWS.", "source": "Bloomberg"},
        {"title": "EU antitrust authorities review Microsoft's partnership with OpenAI.", "source": "Financial Times"},
        {"title": "Microsoft announces $3 billion cybersecurity upgrade across enterprise suite.", "source": "WSJ"},
        {"title": "Cybersecurity breach in core Microsoft services sparks security questions.", "source": "Reuters"}
    ],
    "TSLA": [
        {"title": "Tesla secures massive production expansion approvals for Shanghai Gigafactory.", "source": "Reuters"},
        {"title": "Global EV demand slows as competitors cut prices, pinching Tesla operating margins.", "source": "Bloomberg"},
        {"title": "Elon Musk announces upcoming reveal of fully autonomous robotaxi fleet in August.", "source": "TechCrunch"},
        {"title": "Safety regulators open investigation into Tesla's Full Self-Driving software performance.", "source": "WSJ"},
        {"title": "Tesla shares surge 8% as weekly production targets hit record levels.", "source": "MarketWatch"}
    ],
    "AMZN": [
        {"title": "Amazon AWS launches custom silicon AI chips, offering significant compute savings.", "source": "Bloomberg"},
        {"title": "FTC expands antitrust probe into Amazon's third-party merchant marketplace fees.", "source": "Reuters"},
        {"title": "Retail holiday sales crush expectations, proving prime membership retention.", "source": "WSJ"},
        {"title": "Amazon logistics network optimizes delivery speeds, reducing operating overhead.", "source": "CNBC"}
    ],
    "GOOGL": [
        {"title": "Google launches Gemini 1.5 Pro, offering massive 1-million-token context windows.", "source": "Bloomberg"},
        {"title": "Google search advertising revenue gains momentum, outperforming social media competitors.", "source": "MarketWatch"},
        {"title": "Federal judge rules against Google in milestone DOJ search antitrust case.", "source": "Reuters"},
        {"title": "Alphabet explores multi-billion dollar acquisition of HubSpot to bolster CRM options.", "source": "CNBC"}
    ]
}

def analyze_sentiment(text: str) -> float:
    """Uses VADER to get the compound sentiment score between -1.0 and 1.0"""
    scores = analyzer.polarity_scores(text)
    return scores["compound"]

def fetch_news_and_sentiment(ticker: str) -> Dict[str, Any]:
    """
    Fetches headlines from NewsAPI or falls back to simulated financial headlines.
    Runs VADER sentiment analysis on each headline and computes averages.
    """
    ticker = ticker.upper().strip()
    news_api_key = os.getenv("NEWS_API_KEY")
    
    headlines = []
    
    # If NewsAPI key is configured and valid
    if news_api_key and news_api_key != "mock_key" and news_api_key != "your_news_api_key_here":
        try:
            url = f"https://newsapi.org/v2/everything?q={ticker}+stock+finance&sortBy=publishedAt&pageSize=6&apiKey={news_api_key}"
            response = httpx.get(url, timeout=5.0)
            if response.status_code == 200:
                articles = response.json().get("articles", [])
                for art in articles:
                    title = art.get("title", "")
                    source = art.get("source", {}).get("name", "Unknown Source")
                    if title:
                        headlines.append({
                            "title": title,
                            "source": source
                        })
                logger.info(f"NewsAPI: Successfully retrieved {len(headlines)} fresh articles for {ticker}.")
        except Exception as e:
            logger.warning(f"Failed to query NewsAPI for {ticker}: {e}. Utilizing fallbacks...")

    # Fallback to high-quality mockup headlines if NewsAPI is offline, rate-limited, or unconfigured
    if not headlines:
        mock_list = MOCK_NEWS.get(ticker)
        if mock_list:
            headlines = [{"title": h["title"], "source": h["source"]} for h in mock_list]
        else:
            # Dynamically construct mock headlines for unseeded tickers
            headlines = [
                {"title": f"Analysts update price target for {ticker} following positive quarterly guidance.", "source": "MarketWatch"},
                {"title": f"Market dynamics introduce consolidation pressures for {ticker} and its peers.", "source": "Reuters"},
                {"title": f"Key institutional investors scale up holdings in {ticker} common stock.", "source": "Bloomberg"}
            ]
        logger.info(f"News Tool: Yielded mock fallback data for {ticker}.")

    # Run VADER sentiment scoring on each headline
    total_sentiment = 0.0
    scored_headlines = []
    
    for h in headlines:
        score = analyze_sentiment(h["title"])
        scored_headlines.append({
            "title": h["title"],
            "source": h["source"],
            "sentiment": score
        })
        total_sentiment += score
        
    avg_sentiment = total_sentiment / len(headlines) if headlines else 0.0
    
    # Categorize overall sentiment
    if avg_sentiment >= 0.15:
        category = "Bullish"
    elif avg_sentiment <= -0.15:
        category = "Bearish"
    else:
        category = "Neutral"

    return {
        "headlines": scored_headlines,
        "sentiment_avg": round(avg_sentiment, 3),
        "sentiment_label": category
    }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Executing news_tool.py VADER self-test...")
    test_tickers = ["AAPL", "TSLA", "UNKNOWN"]
    for t in test_tickers:
        res = fetch_news_and_sentiment(t)
        logger.info(f"Ticker: {t} | Label: {res['sentiment_label']} | Avg Score: {res['sentiment_avg']}")
        for idx, h in enumerate(res['headlines'][:2]):
            logger.info(f"  Head {idx+1}: '{h['title']}' (Score: {h['sentiment']:.2f})")
