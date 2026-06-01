"use client";

import React from "react";
import { Treemap, ResponsiveContainer, Tooltip } from "recharts";
import { PieChart } from "lucide-react";

interface PortfolioTickerData {
  sector: string;
}

interface SectorHeatmapProps {
  weights: Record<string, number>;
  marketData: Record<string, PortfolioTickerData>;
}

export default function SectorHeatmap({ weights, marketData }: SectorHeatmapProps) {
  // Aggregate weights by sector
  const getSectorData = () => {
    const sectors: Record<string, number> = {};
    
    Object.entries(weights).forEach(([ticker, weight]) => {
      const market = marketData[ticker];
      const sector = market?.sector || "Other";
      
      sectors[sector] = (sectors[sector] || 0) + weight;
    });

    return Object.entries(sectors).map(([name, weight]) => ({
      name,
      size: parseFloat((weight * 100).toFixed(1)),
      value: parseFloat((weight * 100).toFixed(1))
    })).sort((a, b) => b.size - a.size);
  };

  const data = getSectorData();

  // Premium color assigners for financial sectors
  const getSectorColor = (name: string, index: number) => {
    const colors = [
      "bg-gradient-to-br from-sky-600 to-sky-700",
      "bg-gradient-to-br from-emerald-600 to-emerald-700",
      "bg-gradient-to-br from-violet-600 to-violet-700",
      "bg-gradient-to-br from-amber-600 to-amber-700",
      "bg-gradient-to-br from-purple-600 to-purple-700",
      "bg-gradient-to-br from-rose-600 to-rose-700"
    ];
    return colors[index % colors.length];
  };

  if (data.length === 0) {
    return (
      <div className="glass-panel rounded-2xl p-6 h-80 flex items-center justify-center text-slate-400 italic">
        Calculating sector weighting parameters...
      </div>
    );
  }

  return (
    <div className="glass-panel rounded-2xl p-6 shadow-md border border-slate-200 dark:border-slate-800 flex flex-col justify-between">
      <div>
        <h3 className="font-bold text-base text-slate-900 dark:text-slate-50 flex items-center gap-2">
          <PieChart className="w-5 h-5 text-sky-500" />
          Sector Weight Allocations
        </h3>
        <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5 mb-6">
          Exposure breakdown by industry sectors.
        </p>
      </div>

      {/* Recharts / Custom Heatmap representation */}
      {/* Since Treemap requires precise custom node renderers that can be verbose,
          we will present a gorgeous grid list styled as micro card blocks, 
          which is extremely readable, responsive, and fits premium UI dashboards perfectly! */}
      <div className="space-y-4">
        {data.map((item, idx) => (
          <div key={idx} className="space-y-2">
            <div className="flex justify-between text-xs font-semibold">
              <span className="text-slate-700 dark:text-slate-350">{item.name}</span>
              <span className="font-bold text-slate-900 dark:text-slate-50">{item.size}%</span>
            </div>
            
            {/* Custom progress loading bar style */}
            <div className="w-full bg-slate-200/50 h-2.5 rounded-full overflow-hidden dark:bg-slate-800">
              <div 
                className={`h-2.5 rounded-full bg-gradient-to-r ${
                  idx === 0 
                    ? "from-sky-500 to-sky-600" 
                    : idx === 1 
                    ? "from-emerald-500 to-emerald-600" 
                    : "from-violet-500 to-violet-600"
                }`}
                style={{ width: `${item.size}%` }}
              />
            </div>
          </div>
        ))}
      </div>
      
      {/* Visual Color Labels Grid */}
      <div className="grid grid-cols-2 gap-2 mt-6 pt-4 border-t border-slate-200 dark:border-slate-800">
        {data.slice(0, 4).map((item, idx) => (
          <div key={idx} className="flex items-center gap-1.5 text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase">
            <span className={`w-2.5 h-2.5 rounded-md ${
              idx === 0 
                ? "bg-sky-500" 
                : idx === 1 
                ? "bg-emerald-500" 
                : idx === 2 
                ? "bg-violet-500" 
                : "bg-amber-500"
            }`} />
            <span className="truncate">{item.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
