from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AgentLog(BaseModel):
    agent: str  # "MarketAgent", "SentimentAgent", "ReportAgent"
    phase: str  # "THINK", "DECIDE", "ACT", "OBSERVE", "REPEAT", "COMPLETE"
    message: str
    timestamp: str

class ReportState(BaseModel):
    job_id: str = Field(..., description="Unique job ID for tracking")
    tickers: List[str] = Field(default_factory=list, description="List of stock tickers in the portfolio")
    weights: Dict[str, float] = Field(default_factory=dict, description="Weights mapping for tickers (e.g. {'AAPL': 0.5, 'MSFT': 0.5})")
    
    # Aggregated outputs from Market Agent
    market_data: Dict[str, Any] = Field(default_factory=dict, description="Gathered yfinance statistics and 1y pricing history")
    
    # Aggregated outputs from Sentiment Agent
    sentiment_data: Dict[str, Any] = Field(default_factory=dict, description="News headlines and sentiment analysis scores")
    
    # Analysis outputs
    risk_score: float = Field(0.0, description="Calculated overall portfolio risk rating (1 to 10)")
    report_markdown: str = Field("", description="Final aggregated report markdown written by report_agent")
    
    # Running execution logs
    logs: List[Dict[str, Any]] = Field(default_factory=list, description="Reasoning logs representing the Think-Decide-Act steps")
    
    # Helper metadata
    error: Optional[str] = None
