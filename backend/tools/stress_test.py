import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Core metrics for historical scenarios
# Benchmark S&P 500 returns during these major periods
SCENARIOS = {
    "2008_FINANCIAL_CRISIS": {
        "name": "2008 Financial Crisis",
        "benchmark_return": -50.9,
        "duration": "18 Months (Oct 2007 - Mar 2009)",
        "recovery_benchmark": 37,  # months to break even
        "sector_performance": {
            "Technology": -48.0,
            "Consumer Cyclical": -55.0,
            "Financials": -75.0,
            "Healthcare": -28.0,
            "Utilities": -22.0,
            "Other": -40.0
        },
        "description": "Triggered by subprime mortgages and banking liquidity defaults. High leverage and consumer cyclicals were obliterated, while defensive healthcare and utilities preserved capital."
    },
    "2020_COVID_CRASH": {
        "name": "2020 COVID-19 Crash",
        "benchmark_return": -33.9,
        "duration": "1 Month (Feb 2020 - Mar 2020)",
        "recovery_benchmark": 5,  # months to break even
        "sector_performance": {
            "Technology": -22.0,
            "Consumer Cyclical": -38.0,
            "Financials": -43.0,
            "Healthcare": -18.0,
            "Utilities": -15.0,
            "Other": -30.0
        },
        "description": "A rapid shock triggered by global containment lockdowns. Tech and software services recovered in record time due to work-from-home demand and historic federal reserve rate cuts, while brick-and-mortar cyclicals lagged."
    },
    "DOT_COM_CRASH": {
        "name": "Dot-Com Meltdown (2000)",
        "benchmark_return": -49.1,
        "duration": "30 Months (Mar 2000 - Oct 2002)",
        "recovery_benchmark": 72,  # months to break even
        "sector_performance": {
            "Technology": -82.0,
            "Consumer Cyclical": -42.0,
            "Financials": -12.0,
            "Healthcare": -10.0,
            "Utilities": +5.0,
            "Other": -25.0
        },
        "description": "The popping of highly speculative internet growth evaluations. Tech equities lost over 80% of value, whereas value-anchored traditional assets and utilities acted as solid capital safe havens."
    }
}

def simulate_stress_scenario(
    tickers: List[str],
    weights: Dict[str, float],
    market_data: Dict[str, Any],
    scenario_id: str
) -> Dict[str, Any]:
    """
    Simulates a historical crash scenario for the given portfolio weights.
    Calculates estimated return, drawdown, and recovery times based on sector beta.
    """
    scenario = SCENARIOS.get(scenario_id)
    if not scenario:
        raise ValueError(f"Scenario '{scenario_id}' is not defined.")

    portfolio_return = 0.0
    total_weight = 0.0
    
    for ticker in tickers:
        weight = weights.get(ticker, 0.0)
        market = market_data.get(ticker, {})
        sector = market.get("sector", "Other")
        beta = market.get("beta", 1.0)
        
        # Determine the return of the stock in this crisis
        # It's based on the sector return multiplied/scaled slightly by its individual beta
        sector_ret = scenario["sector_performance"].get(sector)
        if sector_ret is None:
            # Fallback to standard sector index performance
            sector_ret = scenario["sector_performance"].get("Other", -35.0)
            
        # Scale the sector drawdown based on asset beta
        # A beta > 1 increases the negative impact, beta < 1 cushions it
        if sector_ret < 0:
            asset_return = sector_ret * (0.8 + 0.2 * beta)
        else:
            asset_return = sector_ret / (0.8 + 0.2 * beta)
            
        portfolio_return += weight * asset_return
        total_weight += weight

    if total_weight > 0:
        portfolio_return = portfolio_return / total_weight

    # Drawdowns are generally 5% to 15% deeper than the final holding period return
    # due to mid-cycle peak-to-trough movements
    max_drawdown = portfolio_return * 1.15
    max_drawdown = max(-99.9, min(0.0, max_drawdown))  # bound between -100% and 0%
    
    # Calculate recovery speed based on portfolio return
    # Deep drawdowns take exponentially longer to break even
    if portfolio_return > -15:
        recovery_factor = 0.3
    elif portfolio_return > -35:
        recovery_factor = 0.75
    else:
        recovery_factor = 1.3
        
    recovery_months = int(scenario["recovery_benchmark"] * recovery_factor)
    recovery_months = max(1, recovery_months)

    return {
        "scenario_id": scenario_id,
        "name": scenario["name"],
        "duration": scenario["duration"],
        "description": scenario["description"],
        "portfolio_return": round(portfolio_return, 1),
        "benchmark_return": scenario["benchmark_return"],
        "max_drawdown": round(max_drawdown, 1),
        "recovery_months": recovery_months
    }

def run_all_stress_tests(
    tickers: List[str],
    weights: Dict[str, float],
    market_data: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Runs all 3 major stress test scenarios"""
    results = []
    for sc_id in SCENARIOS.keys():
        res = simulate_stress_scenario(tickers, weights, market_data, sc_id)
        results.append(res)
    return results
