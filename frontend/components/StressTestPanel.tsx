"use client";

import React, { useState, useEffect } from "react";
import { ShieldAlert, Zap, RotateCcw, HelpCircle } from "lucide-react";

interface TickerMarketData {
  sector: string;
  beta: number;
}

interface StressTestPanelProps {
  initialWeights: Record<string, number>;
  marketData: Record<string, TickerMarketData>;
}

// Replicate historical crash multipliers in JavaScript for real-time slider calculations
const SCENARIOS = {
  "2008_FINANCIAL_CRISIS": {
    name: "2008 Financial Crisis",
    benchmark_return: -50.9,
    duration: "18 Months (Oct 2007 - Mar 2009)",
    recovery_benchmark: 37,
    sector_performance: {
      "Technology": -48.0,
      "Consumer Cyclical": -55.0,
      "Financials": -75.0,
      "Healthcare": -28.0,
      "Utilities": -22.0,
      "Other": -40.0
    },
    description: "Triggered by subprime mortgages and banking defaults. Highly leveraged growth assets collapsed, whereas defensive healthcare and traditional utilities acted as safe havens."
  },
  "2020_COVID_CRASH": {
    name: "2020 COVID-19 Crash",
    benchmark_return: -33.9,
    duration: "1 Month (Feb 2020 - Mar 2020)",
    recovery_benchmark: 5,
    sector_performance: {
      "Technology": -22.0,
      "Consumer Cyclical": -38.0,
      "Financials": -43.0,
      "Healthcare": -18.0,
      "Utilities": -15.0,
      "Other": -30.0
    },
    description: "A rapid crash driven by global pandemic lockdowns. Software and cloud tech recovered almost instantly due to stimulus liquidity, while travel and brick-and-mortar retail lagged."
  },
  "DOT_COM_CRASH": {
    name: "Dot-Com Meltdown (2000)",
    benchmark_return: -49.1,
    duration: "30 Months (Mar 2000 - Oct 2002)",
    recovery_benchmark: 72,
    sector_performance: {
      "Technology": -82.0,
      "Consumer Cyclical": -42.0,
      "Financials": -12.0,
      "Healthcare": -10.0,
      "Utilities": +5.0,
      "Other": -25.0
    },
    description: "The popping of highly inflated internet equity valuations. Technology growth fell over 80%, while traditional value assets remained flat or preserved capital."
  }
};

type ScenarioKey = keyof typeof SCENARIOS;

export default function StressTestPanel({ initialWeights, marketData }: StressTestPanelProps) {
  const [activeTab, setActiveTab] = useState<ScenarioKey>("2008_FINANCIAL_CRISIS");
  const [simWeights, setSimWeights] = useState<Record<string, number>>({});
  const [isBalanced, setIsBalanced] = useState(true);

  // Initialize weights
  useEffect(() => {
    setSimWeights({ ...initialWeights });
  }, [initialWeights]);

  const tickers = Object.keys(initialWeights);

  const handleSliderChange = (ticker: string, value: number) => {
    const newWeights = { ...simWeights, [ticker]: value / 100 };
    setSimWeights(newWeights);
    
    // Check if weights sum to 100% or close
    const total = Object.values(newWeights).reduce((sum, w) => sum + w, 0);
    setIsBalanced(Math.abs(total - 1.0) < 0.001);
  };

  const resetWeights = () => {
    setSimWeights({ ...initialWeights });
    setIsBalanced(true);
  };

  // Run real-time client-side calculation
  const calculateMetrics = (weightsToUse: Record<string, number>) => {
    const scenario = SCENARIOS[activeTab];
    let portfolioReturn = 0.0;
    let totalWeight = 0.0;
    
    tickers.forEach(t => {
      const weight = weightsToUse[t] || 0;
      const market = marketData[t] || { sector: "Other", beta: 1.0 };
      const sector = market.sector;
      const beta = market.beta;
      
      const sectorRet = scenario.sector_performance[sector as keyof typeof scenario.sector_performance] || scenario.sector_performance["Other"];
      
      let assetReturn = 0;
      if (sectorRet < 0) {
        assetReturn = sectorRet * (0.8 + 0.2 * beta);
      } else {
        assetReturn = sectorRet / (0.8 + 0.2 * beta);
      }
      
      portfolioReturn += weight * assetReturn;
      totalWeight += weight;
    });

    if (totalWeight > 0) {
      portfolioReturn = portfolioReturn / totalWeight;
    }

    const maxDrawdown = portfolioReturn * 1.15;
    
    let recoveryFactor = 0.5;
    if (portfolioReturn > -15) recoveryFactor = 0.3;
    else if (portfolioReturn > -35) recoveryFactor = 0.75;
    else recoveryFactor = 1.3;
    
    const recoveryMonths = Math.max(1, Math.round(scenario.recovery_benchmark * recoveryFactor));

    return {
      portfolioReturn: parseFloat(portfolioReturn.toFixed(1)),
      maxDrawdown: parseFloat(Math.max(-99.9, Math.min(0, maxDrawdown)).toFixed(1)),
      recoveryMonths
    };
  };

  // If weights aren't balanced, we temporarily normalize them for calculation
  const getNormalizedWeights = () => {
    const total = Object.values(simWeights).reduce((sum, w) => sum + w, 0);
    if (total === 0) return simWeights;
    
    const normalized: Record<string, number> = {};
    tickers.forEach(t => {
      normalized[t] = (simWeights[t] || 0) / total;
    });
    return normalized;
  };

  const weightsForCalc = isBalanced ? simWeights : getNormalizedWeights();
  const metrics = calculateMetrics(weightsForCalc);
  const scenario = SCENARIOS[activeTab];

  const totalCurrentWeightPercent = Object.values(simWeights).reduce((sum, w) => sum + w, 0) * 100;

  return (
    <div className="glass-panel rounded-2xl p-6 shadow-md border border-slate-200 dark:border-slate-800 grid grid-cols-1 lg:grid-cols-12 gap-6">
      
      {/* 1. Left Side: Scenario description & tabs (7 cols) */}
      <div className="lg:col-span-7 flex flex-col justify-between space-y-6">
        <div>
          <h3 className="font-bold text-base text-slate-900 dark:text-slate-50 flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-amber-500" />
            Macro Stress Simulator
          </h3>
          <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">
            Test how different weights survive major historical financial downturns.
          </p>
        </div>

        {/* Tab triggers */}
        <div className="flex border-b border-slate-200 dark:border-slate-800 text-xs font-bold uppercase tracking-wider">
          {(Object.keys(SCENARIOS) as ScenarioKey[]).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-3 pr-4 first:pl-0 border-b-2 transition-all ${
                activeTab === tab
                  ? "border-sky-500 text-sky-600 dark:text-sky-400"
                  : "border-transparent text-slate-400 hover:text-slate-600 dark:hover:text-slate-350"
              }`}
            >
              {SCENARIOS[tab].name}
            </button>
          ))}
        </div>

        {/* Selected Scenario details */}
        <div className="space-y-3">
          <span className="text-[9px] font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500">Scenario Context</span>
          <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 leading-relaxed bg-slate-100/50 dark:bg-slate-900/50 p-4 rounded-xl border border-slate-200/50 dark:border-slate-800">
            {scenario.description}
          </p>
          <span className="text-[10px] text-slate-400 block dark:text-slate-500">
            <b>Historical S&P 500 Drawdown:</b> {scenario.benchmark_return}% over {scenario.duration}
          </span>
        </div>

        {/* Stress Metrics Cards */}
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-slate-100/40 border border-slate-200/50 p-3.5 rounded-xl text-center dark:bg-slate-900/40 dark:border-slate-850">
            <span className="text-[9px] font-bold text-slate-400 block dark:text-slate-500 uppercase tracking-widest">Sim Return</span>
            <span className={`text-sm font-black tracking-tight ${metrics.portfolioReturn >= 0 ? "text-emerald-500" : "text-red-500"}`}>
              {metrics.portfolioReturn}%
            </span>
          </div>
          
          <div className="bg-slate-100/40 border border-slate-200/50 p-3.5 rounded-xl text-center dark:bg-slate-900/40 dark:border-slate-850">
            <span className="text-[9px] font-bold text-slate-400 block dark:text-slate-500 uppercase tracking-widest">Max Drawdown</span>
            <span className="text-sm font-black tracking-tight text-red-500">
              {metrics.maxDrawdown}%
            </span>
          </div>

          <div className="bg-slate-100/40 border border-slate-200/50 p-3.5 rounded-xl text-center dark:bg-slate-900/40 dark:border-slate-850">
            <span className="text-[9px] font-bold text-slate-400 block dark:text-slate-500 uppercase tracking-widest">Recovery time</span>
            <span className="text-sm font-black tracking-tight text-amber-500">
              {metrics.recoveryMonths} Mo
            </span>
          </div>
        </div>
      </div>

      {/* 2. Right Side: Interactive Sliders (5 cols) */}
      <div className="lg:col-span-5 flex flex-col justify-between border-t lg:border-t-0 lg:border-l border-slate-200 dark:border-slate-800 pt-6 lg:pt-0 lg:pl-6 space-y-6">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 flex items-center gap-1">
            <Zap className="w-3.5 h-3.5 text-sky-500" />
            What-If Weight Sliders
          </span>
          
          <button
            onClick={resetWeights}
            className="text-[10px] font-bold text-slate-400 hover:text-sky-500 flex items-center gap-1 bg-slate-100/50 px-2 py-1 rounded-md dark:bg-slate-900/50 border border-slate-200/25"
            title="Reset to default allocations"
          >
            <RotateCcw className="w-3 h-3" />
            Reset
          </button>
        </div>

        {/* Sliders loop */}
        <div className="space-y-4">
          {tickers.map((t) => {
            const currentWeight = (simWeights[t] || 0) * 100;
            return (
              <div key={t} className="space-y-1">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-slate-700 dark:text-slate-300 tracking-wider font-bold">{t}</span>
                  <span className="text-slate-900 dark:text-slate-100 font-extrabold">{currentWeight.toFixed(0)}%</span>
                </div>
                
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={currentWeight}
                  onChange={(e) => handleSliderChange(t, parseInt(e.target.value))}
                  className="w-full h-1.5 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-sky-500 focus:outline-none"
                />
              </div>
            );
          })}
        </div>

        {/* Weight Balance feedback block */}
        <div className="pt-4 border-t border-slate-200 dark:border-slate-800 flex flex-col space-y-2">
          <div className="flex justify-between text-xs font-bold text-slate-400 dark:text-slate-500">
            <span>Simulated Sum:</span>
            <span className={isBalanced ? "text-emerald-500" : "text-amber-500"}>
              {totalCurrentWeightPercent.toFixed(0)}%
            </span>
          </div>

          {!isBalanced && (
            <div className="bg-amber-500/10 border border-amber-500/20 text-amber-600 dark:text-amber-400 text-[10px] p-2.5 rounded-lg flex items-start gap-1.5 leading-relaxed">
              <Zap className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" />
              <p className="font-semibold">
                Sliders do not equal 100%. Calculating using proportional relative normalized weights.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
