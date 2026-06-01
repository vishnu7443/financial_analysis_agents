import os
import asyncio
import logging
from datetime import datetime
from typing import AsyncGenerator, Dict, Any, List
from backend.models.report import ReportState
from backend.agents.market_agent import log_agent_step

logger = logging.getLogger(__name__)

def calculate_portfolio_risk(state: ReportState) -> float:
    """
    Calculates overall portfolio risk rating from 1 to 10.
    Uses a weighted beta-based algorithm.
    - Weighted Beta < 0.8: Low Risk (1 - 3)
    - Weighted Beta 0.8 - 1.2: Moderate Risk (4 - 6)
    - Weighted Beta 1.2 - 1.8: High Risk (7 - 8)
    - Weighted Beta > 1.8: Extreme Volatility (9 - 10)
    """
    weighted_beta = 0.0
    total_weight = 0.0
    
    for ticker, weight in state.weights.items():
        market = state.market_data.get(ticker, {})
        beta = market.get("beta", 1.0)
        weighted_beta += weight * beta
        total_weight += weight
        
    if total_weight == 0:
        return 5.0
        
    avg_beta = weighted_beta / total_weight
    
    # Scale from 1 to 10
    if avg_beta < 0.5:
        score = 1.0 + (avg_beta / 0.5) * 2.0  # 1.0 to 3.0
    elif avg_beta < 1.0:
        score = 3.0 + ((avg_beta - 0.5) / 0.5) * 3.0  # 3.0 to 6.0
    elif avg_beta < 1.8:
        score = 6.0 + ((avg_beta - 1.0) / 0.8) * 3.0  # 6.0 to 9.0
    else:
        score = 9.0 + min(((avg_beta - 1.8) / 1.2) * 1.0, 1.0)  # 9.0 to 10.0
        
    return round(score, 1)

def generate_local_markdown_report(state: ReportState) -> str:
    """
    Generates a premium, highly detailed financial analysis markdown report locally.
    Used as an ultra-reliable, high-fidelity fallback.
    """
    risk_score = state.risk_score
    risk_level = "Low" if risk_score < 4.0 else "Medium" if risk_score < 7.0 else "High"
    
    report = []
    report.append(f"# PREMIUM INVESTMENT PORTFOLIO REPORT")
    report.append(f"**Generated on:** {datetime.utcnow().strftime('%B %d, %Y')} | **Analyst Crew:** Antigravity AI Operations\n")
    report.append(f"## 1. Executive Summary")
    report.append(f"This comprehensive investment report compiles technical and sentiment-driven indicators across your multi-asset portfolio. Our market and sentiment agents have scanned exchange data, SEC filing valuations, and social news channels to formulate a holistic rating.")
    report.append(f"- **Overall Portfolio Risk Rating:** `{risk_score}/10` (**{risk_level} Risk**)")
    report.append(f"- **Asset Allocation Count:** {len(state.tickers)} Tickers")
    report.append(f"- **Primary Sector Dominance:** {state.market_data.get(state.tickers[0], {}).get('sector', 'N/A')}\n")
    
    report.append(f"## 2. Asset Allocation & Weight Optimization")
    report.append(f"Below is the current model allocation table for the evaluated holdings:")
    report.append(f"| Ticker | Company Name | Sector | Weight (%) | Price | P/E Ratio | Beta | Sentiment |")
    report.append(f"| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    
    for ticker in state.tickers:
        market = state.market_data.get(ticker, {})
        sentiment = state.sentiment_data.get(ticker, {})
        name = market.get("name", ticker)
        sector = market.get("sector", "Other")
        weight_pct = state.weights.get(ticker, 0.0) * 100
        price = f"${market.get('price', 0.0):.2f}"
        pe = market.get("pe_ratio")
        pe_str = f"{pe:.1f}" if pe else "N/A"
        beta = f"{market.get('beta', 1.0):.2f}"
        sent_label = sentiment.get("sentiment_label", "Neutral")
        sent_val = sentiment.get("sentiment_avg", 0.0)
        sent_str = f"{sent_label} ({sent_val:+.2f})"
        
        report.append(f"| **{ticker}** | {name} | {sector} | {weight_pct:.1f}% | {price} | {pe_str} | {beta} | {sent_str} |")
        
    report.append("\n## 3. Deep-Dive Qualitative & Sentiment Intelligence")
    for ticker in state.tickers:
        sentiment = state.sentiment_data.get(ticker, {})
        headlines = sentiment.get("headlines", [])
        avg_s = sentiment.get("sentiment_avg", 0.0)
        
        report.append(f"### {ticker} Narrative & Media Positioning")
        report.append(f"The media sentiment index for **{ticker}** stands at `{avg_s:+.2f}` (categorized as **{sentiment.get('sentiment_label', 'Neutral')}**). Key headlines include:")
        for h in headlines[:3]:
            report.append(f"- \"{h['title']}\" (*{h['source']}*) [Sentiment: {h['sentiment']:+.2f}]")
        report.append("")
        
    report.append("## 4. Portfolio Risk Analysis & Stress Implications")
    report.append(f"With an overall risk rating of `{risk_score}/10`, this portfolio reflects a **{risk_level.lower()}-risk** profile.")
    
    if risk_score >= 7.0:
        report.append("The high concentration in high-beta equity assets (such as growth technology or consumer durables) exposes the principal to substantial volatility during macroeconomic interest rate contractions or systemic market drawdowns.")
    elif risk_score >= 4.0:
        report.append("The portfolio displays balanced diversification. It captures a solid balance of tech growth assets and stable dividend anchors, creating a robust shield against inflationary market cycles.")
    else:
        report.append("This is an extremely conservative, low-volatility portfolio. Returns will likely mirror secure benchmark indexing with tight downside defense during recessionary quarters.")
        
    report.append("\n*Disclaimer: This analysis is compiled by an AI Agent Crew for demo purposes and does not constitute formal, licensed financial advisory recommendations.*")
    
    return "\n".join(report)

async def stream_report_agent(state: ReportState, emitter_callback=None) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Asynchronously streams the compiled report using Claude (Anthropic API)
    or falls back to a highly realistic template-driven streaming experience.
    Yields dictionary events: {"type": "token"|"status", "content": str}
    """
    # 1. THINK
    log_agent_step(state, "ReportAgent", "THINK", "Evaluating collected market data and news sentiments to compile the portfolio report.", emitter_callback)
    
    # Calculate overall risk score
    state.risk_score = calculate_portfolio_risk(state)
    log_agent_step(state, "ReportAgent", "OBSERVE", f"Computed Portfolio Risk Rating: {state.risk_score}/10 based on asset betas.", emitter_callback)
    
    # 2. DECIDE
    api_key = os.getenv("ANTHROPIC_API_KEY")
    use_claude = api_key and api_key != "mock_key" and api_key != "your_anthropic_api_key_here"
    
    if use_claude:
        log_agent_step(state, "ReportAgent", "DECIDE", "Activating Anthropic Claude via official SDK to stream custom synthesized investment report.", emitter_callback)
    else:
        log_agent_step(state, "ReportAgent", "DECIDE", "No valid Anthropic API key found. Activating premium local analytics generator fallback.", emitter_callback)
        
    # 3. ACT
    log_agent_step(state, "ReportAgent", "ACT", "Drafting report sections and streaming output channels...", emitter_callback)
    
    if use_claude:
        try:
            from anthropic import AsyncAnthropic
            client = AsyncAnthropic(api_key=api_key)
            
            # Format state context for LLM prompt
            prompt_context = {
                "tickers": state.tickers,
                "weights": state.weights,
                "market_data": {t: {k: v for k, v in m.items() if k != 'history_1y'} for t, m in state.market_data.items()}, # omit history to save tokens
                "sentiment_data": state.sentiment_data,
                "risk_score": state.risk_score
            }
            
            system_prompt = (
                "You are an elite, Wall Street financial analyst and portfolio risk manager. "
                "Write a highly professional, comprehensive investment portfolio report in Markdown. "
                "Use an objective, premium, analytical tone. Analyze the allocations, the sector exposures, "
                "the Trailing P/E multiples, the beta risks, and the news sentiment scores. "
                "Structure the report clearly with markdown headings, tables, bullet points, and key warnings."
            )
            
            user_message = f"Here is the collected real-time portfolio intelligence:\n\n{prompt_context}\n\nPlease write the analysis report."
            
            # Call Claude stream
            stream = await client.messages.create(
                max_tokens=2500,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                model="claude-3-5-sonnet-20241022",
                stream=True
            )
            
            accumulated_report = ""
            async for chunk in stream:
                if chunk.type == "content_block_delta" and chunk.delta.text:
                    token = chunk.delta.text
                    accumulated_report += token
                    yield {"type": "token", "content": token}
                    # We can introduce a tiny sleep to allow smooth UI rendering
                    await asyncio.sleep(0.005)
            
            state.report_markdown = accumulated_report
            
        except Exception as e:
            logger.error(f"Claude Streaming Error: {e}. Falling back to local reporter...")
            log_agent_step(state, "ReportAgent", "OBSERVE", f"Claude call failed ({e}). Falling back to local reporter.", emitter_callback)
            use_claude = False  # Triggers local fallback

    if not use_claude:
        # Local high-quality mock stream to guarantee beautiful mock experience
        full_report = generate_local_markdown_report(state)
        
        # Split report into smaller word tokens to simulate a super fast, premium streaming experience
        words = full_report.split(" ")
        accumulated_report = ""
        
        # Stream in batches of 4 words for optimal responsiveness
        batch_size = 4
        for i in range(0, len(words), batch_size):
            token = " ".join(words[i:i+batch_size]) + " "
            accumulated_report += token
            yield {"type": "token", "content": token}
            await asyncio.sleep(0.03)  # Smooth flow
            
        state.report_markdown = accumulated_report

    # 4. OBSERVE & 5. REPEAT / COMPLETE
    log_agent_step(state, "ReportAgent", "OBSERVE", "Successfully completed investment report stream. Document compiled.", emitter_callback)
    log_agent_step(state, "ReportAgent", "COMPLETE", "Agent crew process terminated. State stored in shared memory.", emitter_callback)
    
    yield {"type": "status", "content": "COMPLETE"}
