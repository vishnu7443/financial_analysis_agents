import asyncio
import sys
import os

# Adjust path to import backend modules properly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.orchestrator import build_and_run_analysis_graph
from backend.tools.stress_test import run_all_stress_tests

async def main():
    print("====================================================")
    print("RUNNING MULTI-AGENT COMPARISON: TWO VARIATIONS")
    print("====================================================")
    
    # 1. Setup Variation A: High-Risk Growth (Heavy TSLA)
    var_a_tickers = ["AAPL", "MSFT", "TSLA"]
    var_a_weights = {"AAPL": 0.10, "MSFT": 0.10, "TSLA": 0.80}
    
    # 2. Setup Variation B: Conservative Growth (Heavy AAPL/MSFT, light TSLA)
    var_b_tickers = ["AAPL", "MSFT", "TSLA"]
    var_b_weights = {"AAPL": 0.45, "MSFT": 0.45, "TSLA": 0.10}
    
    # Run Variation A
    print("\n[Executing Variation A: Growth & High Beta (80% TSLA)...]")
    res_a = await build_and_run_analysis_graph(
        job_id="variation-a-test",
        tickers=var_a_tickers,
        weights=var_a_weights,
        emitter_callback=lambda x: None  # suppress SSE logs for clean output
    )
    
    # Run Variation B
    print("[Executing Variation B: Defensive Tech (45% AAPL, 45% MSFT, 10% TSLA)...]")
    res_b = await build_and_run_analysis_graph(
        job_id="variation-b-test",
        tickers=var_b_tickers,
        weights=var_b_weights,
        emitter_callback=lambda x: None  # suppress SSE logs for clean output
    )
    
    # Run Stress Tests
    stress_a = run_all_stress_tests(var_a_tickers, var_a_weights, res_a.market_data)
    stress_b = run_all_stress_tests(var_b_tickers, var_b_weights, res_b.market_data)
    
    print("\n====================================================")
    print("RESULTS COMPARISON TABLE")
    print("====================================================")
    print(f"| Metric | Variation A (High Beta) | Variation B (Conservative) |")
    print(f"| :--- | :--- | :--- |")
    print(f"| **Portfolio Weights** | AAPL: 10%, MSFT: 10%, TSLA: 80% | AAPL: 45%, MSFT: 45%, TSLA: 10% |")
    print(f"| **Calculated Risk Rating** | {res_a.risk_score}/10 | {res_b.risk_score}/10 |")
    print(f"| **Report Length** | {len(res_a.report_markdown)} chars | {len(res_b.report_markdown)} chars |")
    
    print("\n--- HISTORICAL STRESS TEST PROJECTED DRAWDOWN ---")
    for sa, sb in zip(stress_a, stress_b):
        name = sa["name"]
        print(f"\nScenario: **{name}**")
        print(f"  - Var A: Return: {sa['portfolio_return']}%  | Max Drawdown: {sa['max_drawdown']}% | Recovery: {sa['recovery_months']} months")
        print(f"  - Var B: Return: {sb['portfolio_return']}%  | Max Drawdown: {sb['max_drawdown']}% | Recovery: {sb['recovery_months']} months")

if __name__ == "__main__":
    asyncio.run(main())
