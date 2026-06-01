"use client";

import React from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from "recharts";
import { TrendingUp } from "lucide-react";

interface HistoryPoint {
  date: string;
  close: number;
}

interface TickerMarketData {
  price: number;
  history_1y: HistoryPoint[];
  name: string;
}

interface PortfolioChartProps {
  marketData: Record<string, TickerMarketData>;
  weights: Record<string, number>;
}

export default function PortfolioChart({ marketData, weights }: PortfolioChartProps) {
  // Aggregate and compute cumulative portfolio returns
  const generateChartData = () => {
    // 1. Get dates from standard ticker (e.g. AAPL)
    const activeTickers = Object.keys(weights).filter(t => marketData[t] && marketData[t].history_1y?.length > 0);
    if (activeTickers.length === 0) {
      return [];
    }

    const firstTicker = activeTickers[0];
    const benchmarkTicker = "^GSPC";
    const historyLength = marketData[firstTicker].history_1y.length;
    
    const chartData = [];

    // Extract starting prices for normalization (day 0 = 100%)
    const startPrices: Record<string, number> = {};
    activeTickers.forEach(t => {
      startPrices[t] = marketData[t].history_1y[0].close;
    });

    const startBenchmark = marketData[benchmarkTicker]?.history_1y?.[0]?.close || 1;

    for (let i = 0; i < historyLength; i++) {
      const date = marketData[firstTicker].history_1y[i].date;
      
      // Calculate normalized portfolio return
      let portfolioValue = 0.0;
      activeTickers.forEach(t => {
        const weight = weights[t] || 0;
        const currentPrice = marketData[t].history_1y[i].close;
        const startPrice = startPrices[t] || 1;
        const relativeReturn = (currentPrice / startPrice) - 1.0;
        portfolioValue += weight * relativeReturn;
      });

      // Calculate benchmark return
      const currentBenchmark = marketData[benchmarkTicker]?.history_1y?.[i]?.close || 0;
      const benchmarkReturn = (currentBenchmark / startBenchmark) - 1.0;

      chartData.push({
        date: new Date(date).toLocaleDateString(undefined, { month: "short", day: "numeric" }),
        "Your Portfolio": parseFloat((portfolioValue * 100).toFixed(1)),
        "S&P 500 Index": parseFloat((benchmarkReturn * 100).toFixed(1))
      });
    }

    return chartData;
  };

  const data = generateChartData();

  if (data.length === 0) {
    return (
      <div className="glass-panel rounded-2xl p-6 h-80 flex items-center justify-center text-slate-400 italic">
        Gathering historical trendlines...
      </div>
    );
  }

  // Calculate final absolute returns
  const finalPortReturn = data[data.length - 1]["Your Portfolio"];
  const finalBenchReturn = data[data.length - 1]["S&P 500 Index"];

  return (
    <div className="glass-panel rounded-2xl p-6 shadow-md border border-slate-200 dark:border-slate-800">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
        <div>
          <h3 className="font-bold text-base text-slate-900 dark:text-slate-50 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-sky-500" />
            1-Year Cumulative Performance
          </h3>
          <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">
            Normalized cumulative returns compared to S&P 500 index.
          </p>
        </div>
        
        <div className="flex items-center gap-4 bg-slate-100/50 dark:bg-slate-900/50 p-2.5 rounded-xl border border-slate-200/50 dark:border-slate-800">
          <div className="text-right">
            <span className="text-[10px] font-bold text-slate-400 block dark:text-slate-500 uppercase">Portfolio Return</span>
            <span className={`text-sm font-black tracking-tight ${finalPortReturn >= 0 ? "text-emerald-500" : "text-red-500"}`}>
              {finalPortReturn >= 0 ? "+" : ""}{finalPortReturn}%
            </span>
          </div>
          <div className="border-l border-slate-200 dark:border-slate-800 h-6" />
          <div className="text-right">
            <span className="text-[10px] font-bold text-slate-400 block dark:text-slate-500 uppercase">Benchmark Return</span>
            <span className={`text-sm font-bold tracking-tight ${finalBenchReturn >= 0 ? "text-emerald-500" : "text-red-500"}`}>
              {finalBenchReturn >= 0 ? "+" : ""}{finalBenchReturn}%
            </span>
          </div>
        </div>
      </div>

      <div className="h-72 w-full text-xs font-semibold select-none">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorPort" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#0284c7" stopOpacity={0.2}/>
                <stop offset="95%" stopColor="#0284c7" stopOpacity={0.0}/>
              </linearGradient>
              <linearGradient id="colorBench" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.1}/>
                <stop offset="95%" stopColor="#10b981" stopOpacity={0.0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" opacity={0.6} />
            <XAxis
              dataKey="date"
              stroke="#64748b"
              tickLine={false}
              axisLine={false}
              dy={10}
            />
            <YAxis
              stroke="#64748b"
              tickLine={false}
              axisLine={false}
              dx={-5}
              tickFormatter={(value) => `${value}%`}
            />
            <Tooltip
              contentStyle={{
                background: "rgba(15, 23, 42, 0.95)",
                border: "1px solid #1e293b",
                borderRadius: "12px",
                color: "#f8fafc"
              }}
              labelStyle={{ fontWeight: "bold", paddingBottom: "4px" }}
            />
            <Legend verticalAlign="top" height={36} iconType="circle" />
            <Area
              name="Your Portfolio"
              type="monotone"
              dataKey="Your Portfolio"
              stroke="#0284c7"
              strokeWidth={2.5}
              fillOpacity={1}
              fill="url(#colorPort)"
            />
            <Area
              name="S&P 500 Index"
              type="monotone"
              dataKey="S&P 500 Index"
              stroke="#10b981"
              strokeWidth={1.5}
              strokeDasharray="4 4"
              fillOpacity={1}
              fill="url(#colorBench)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
