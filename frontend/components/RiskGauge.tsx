"use client";

import React, { useEffect, useState } from "react";
import { Shield } from "lucide-react";

interface RiskGaugeProps {
  score: number; // 1 to 10
}

export default function RiskGauge({ score }: RiskGaugeProps) {
  const [animatedScore, setAnimatedScore] = useState(0);

  // Trigger smooth pointer needle entry sweep animation
  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedScore(score);
    }, 150);
    return () => clearTimeout(timer);
  }, [score]);

  // SVG dimensions
  const width = 200;
  const height = 120;
  const radius = 80;
  const cx = width / 2;
  const cy = height - 10;
  
  // Calculate needle coordinates
  // Range is 180 degrees (from Left to Right)
  // 1 -> 180 degrees (Math.PI)
  // 10 -> 0 degrees (0)
  const scorePercent = (animatedScore - 1) / 9; // 0 to 1
  const angle = Math.PI - (scorePercent * Math.PI); // Angle in radians
  
  const needleLength = radius - 15;
  const needleX = cx + needleLength * Math.cos(angle);
  const needleY = cy - needleLength * Math.sin(angle);

  // Determine risk categories
  const getRiskLabel = (s: number) => {
    if (s < 4.0) return { text: "Low Volatility", color: "text-emerald-500", bg: "bg-emerald-500/10" };
    if (s < 7.0) return { text: "Moderate Volatility", color: "text-amber-500", bg: "bg-amber-500/10" };
    if (s < 9.0) return { text: "High Volatility", color: "text-rose-500", bg: "bg-rose-500/10" };
    return { text: "Extreme Volatility", color: "text-purple-500", bg: "bg-purple-500/10" };
  };

  const labelInfo = getRiskLabel(score);

  return (
    <div className="glass-panel rounded-2xl p-6 shadow-md border border-slate-200 dark:border-slate-800 flex flex-col items-center justify-between h-full">
      <div className="w-full text-left self-start">
        <h3 className="font-bold text-base text-slate-900 dark:text-slate-50 flex items-center gap-2">
          <Shield className="w-5 h-5 text-sky-500" />
          Volatility Risk Rating
        </h3>
        <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5 mb-2">
          Portfolio beta aggregate risk score.
        </p>
      </div>

      {/* SVG Arc Gauge */}
      <div className="relative select-none my-4">
        <svg width={width} height={height} className="overflow-visible">
          <defs>
            {/* Emerald to Orange to Red metallic gradient */}
            <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#10b981" />   {/* Emerald 500 */}
              <stop offset="50%" stopColor="#f59e0b" />  {/* Amber 500 */}
              <stop offset="100%" stopColor="#f43f5e" /> {/* Rose 500 */}
            </linearGradient>
            <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
              <feDropShadow dx="0" dy="2" stdDeviation="3" floodOpacity="0.15" />
            </filter>
          </defs>
          
          {/* Background track arc */}
          <path
            d={`M ${cx - radius} ${cy} A ${radius} ${radius} 0 0 1 ${cx + radius} ${cy}`}
            fill="none"
            stroke="var(--border)"
            strokeWidth="12"
            strokeLinecap="round"
            style={{ opacity: 0.4 }}
          />

          {/* Color filled track arc */}
          <path
            d={`M ${cx - radius} ${cy} A ${radius} ${radius} 0 0 1 ${cx + radius} ${cy}`}
            fill="none"
            stroke="url(#gaugeGradient)"
            strokeWidth="12"
            strokeLinecap="round"
          />

          {/* Center cap anchor */}
          <circle cx={cx} cy={cy} r="8" fill="var(--foreground)" />
          <circle cx={cx} cy={cy} r="4" fill="var(--background)" />

          {/* Sweeping pointer needle */}
          <line
            x1={cx}
            y1={cy}
            x2={needleX}
            y2={needleY}
            stroke="var(--foreground)"
            strokeWidth="3.5"
            strokeLinecap="round"
            filter="url(#shadow)"
            style={{ transition: "all 0.8s cubic-bezier(0.34, 1.56, 0.64, 1)" }}
          />
        </svg>

        {/* Center Score badge */}
        <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 flex flex-col items-center">
          <span className="text-3xl font-black tracking-tight">{score.toFixed(1)}</span>
          <span className="text-[9px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest block -mt-1">
            Risk Score
          </span>
        </div>
      </div>

      {/* Description tag */}
      <div className={`mt-2 px-3 py-1.5 rounded-xl border border-slate-200/20 text-xs font-bold uppercase tracking-wider ${labelInfo.bg} ${labelInfo.color}`}>
        {labelInfo.text}
      </div>
    </div>
  );
}
