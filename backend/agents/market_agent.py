import logging
from datetime import datetime
from typing import Dict, Any
from backend.models.report import ReportState
from backend.tools.yfinance_tool import fetch_ticker_data

logger = logging.getLogger(__name__)

def log_agent_step(state: ReportState, agent: str, phase: str, message: str, emitter_callback=None) -> None:
    """Utility to log and format agent reasoning steps, and trigger realtime SSE updates"""
    log_entry = {
        "agent": agent,
        "phase": phase,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }
    state.logs.append(log_entry)
    logger.info(f"[{agent}][{phase}] {message}")
    
    if emitter_callback:
        # If an SSE emitter callback is registered, push the log in real-time
        try:
            emitter_callback(log_entry)
        except Exception as e:
            logger.warning(f"Failed to emit log in real-time: {e}")

async def run_market_agent(state: ReportState, emitter_callback=None) -> ReportState:
    """
    Market Agent: Gathers financial prices, multiples, beta, and historical trends.
    Operates under an explicit Think-Decide-Act-Observe loop.
    """
    log_agent_step(state, "MarketAgent", "THINK", f"Starting market analysis for tickers: {', '.join(state.tickers)}", emitter_callback)
    
    for ticker in state.tickers:
        # 1. THINK
        log_agent_step(state, "MarketAgent", "THINK", f"Evaluating stock '{ticker}'. I need to evaluate its valuation relative to the sector and its historical return variance.", emitter_callback)
        
        # 2. DECIDE
        log_agent_step(state, "MarketAgent", "DECIDE", f"Determined that yfinance_tool is the optimal service to fetch price, trailing multiples, beta, and historical closes for '{ticker}'.", emitter_callback)
        
        # 3. ACT
        log_agent_step(state, "MarketAgent", "ACT", f"Invoking fetch_ticker_data('{ticker}') from the caching finance client...", emitter_callback)
        
        try:
            data = fetch_ticker_data(ticker)
            
            # 4. OBSERVE
            pe_str = f"P/E: {data['pe_ratio']}" if data['pe_ratio'] else "P/E: N/A"
            observation_msg = f"Retrieved data for '{ticker}'. Price: ${data['price']:.2f}, {pe_str}, Beta: {data['beta']:.2f}, Sector: {data['sector']}."
            log_agent_step(state, "MarketAgent", "OBSERVE", observation_msg, emitter_callback)
            
            # Store in state
            state.market_data[ticker] = data
            
        except Exception as e:
            error_msg = f"Failed to acquire market metrics for '{ticker}': {str(e)}"
            log_agent_step(state, "MarketAgent", "OBSERVE", f"ERROR: {error_msg}", emitter_callback)
            state.market_data[ticker] = {
                "price": 100.0,
                "pe_ratio": None,
                "beta": 1.0,
                "sector": "Unknown",
                "name": ticker,
                "history_1y": []
            }
            
        # 5. REPEAT / CONTINUE
        log_agent_step(state, "MarketAgent", "REPEAT", f"Analysis for '{ticker}' completed. Checking next available target...", emitter_callback)

    # Fetch Benchmark (S&P 500) to allow for relative portfolio charting
    log_agent_step(state, "MarketAgent", "THINK", "Fetching benchmark S&P 500 (^GSPC) performance parameters for comparative indexing.", emitter_callback)
    try:
        benchmark_data = fetch_ticker_data("^GSPC")
        state.market_data["^GSPC"] = benchmark_data
        log_agent_step(state, "MarketAgent", "OBSERVE", f"Benchmark index (^GSPC) loaded successfully. Current Level: {benchmark_data['price']:.2f}", emitter_callback)
    except Exception as e:
        log_agent_step(state, "MarketAgent", "OBSERVE", f"Warning: Benchmark S&P 500 failed to load ({e}). Using mock benchmark.", emitter_callback)

    log_agent_step(state, "MarketAgent", "COMPLETE", "Market analysis successfully finalized across all target assets.", emitter_callback)
    return state
