"use client";

import React, { useState } from "react";
import { Plus, Trash2, ShieldAlert, Cpu, Sparkles } from "lucide-react";

interface TickerRow {
  ticker: string;
  weight: number;
}

interface PortfolioInputProps {
  onSubmit: (portfolio: { name: string; tickers: TickerRow[] }) => void;
  isLoading: boolean;
}

export default function PortfolioInput({ onSubmit, isLoading }: PortfolioInputProps) {
  const [portfolioName, setPortfolioName] = useState("Growth Equity Portfolio");
  const [rows, setRows] = useState<TickerRow[]>([
    { ticker: "AAPL", weight: 40 },
    { ticker: "MSFT", weight: 40 },
    { ticker: "TSLA", weight: 20 },
  ]);
  const [error, setError] = useState<string | null>(null);

  const addRow = () => {
    if (rows.length >= 8) {
      setError("Maximum of 8 tickers supported in this MVP.");
      return;
    }
    setRows([...rows, { ticker: "", weight: 0 }]);
    setError(null);
  };

  const removeRow = (index: number) => {
    if (rows.length <= 1) {
      setError("Portfolio must contain at least one ticker.");
      return;
    }
    const newRows = [...rows];
    newRows.splice(index, 1);
    setRows(newRows);
    setError(null);
  };

  const handleTickerChange = (index: number, val: string) => {
    const newRows = [...rows];
    newRows[index].ticker = val.toUpperCase().replace(/[^A-Z^]/g, "");
    setRows(newRows);
    setError(null);
  };

  const handleWeightChange = (index: number, val: string) => {
    const num = parseFloat(val) || 0;
    const newRows = [...rows];
    newRows[index].weight = Math.max(0, Math.min(100, num));
    setRows(newRows);
    setError(null);
  };

  const totalWeight = rows.reduce((sum, r) => sum + r.weight, 0);

  const fillBalancedDefault = () => {
    setRows([
      { ticker: "AAPL", weight: 35 },
      { ticker: "MSFT", weight: 35 },
      { ticker: "TSLA", weight: 10 },
      { ticker: "AMZN", weight: 10 },
      { ticker: "GOOGL", weight: 10 },
    ]);
    setError(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Clean and validate rows
    const cleanedRows = rows.map(r => ({
      ticker: r.ticker.trim().toUpperCase(),
      weight: r.weight
    })).filter(r => r.ticker !== "");

    if (cleanedRows.length === 0) {
      setError("Please add at least one stock ticker symbol.");
      return;
    }

    // Verify weight sums exactly to 100% or 1.0
    // We allow a very small float buffer
    if (Math.abs(totalWeight - 100) > 0.01 && Math.abs(totalWeight - 1.0) > 0.0001) {
      setError(`Total weight must equal 100% (currently ${totalWeight}%). Adjust weights before submitting.`);
      return;
    }

    setError(null);
    onSubmit({ name: portfolioName, tickers: cleanedRows });
  };

  return (
    <div className="glass-panel rounded-2xl p-6 md:p-8 gradient-border-card max-w-2xl mx-auto w-full transition-all duration-300">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-slate-900 dark:text-slate-50 flex items-center gap-2">
            <Cpu className="h-5 w-5 text-sky-500" />
            Configure Analyst Inputs
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Specify stock symbols and weight allocations.
          </p>
        </div>
        <button
          type="button"
          onClick={fillBalancedDefault}
          className="text-xs font-semibold text-sky-600 dark:text-sky-400 hover:underline flex items-center gap-1 border border-sky-500/10 bg-sky-500/5 px-2.5 py-1.5 rounded-lg"
        >
          <Sparkles className="w-3.5 h-3.5" />
          Prefill 5 Tickers
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Portfolio Title input */}
        <div className="space-y-2">
          <label className="text-xs font-bold uppercase tracking-wider text-slate-400 block dark:text-slate-500">
            Portfolio Label
          </label>
          <input
            type="text"
            value={portfolioName}
            onChange={(e) => setPortfolioName(e.target.value)}
            className="w-full bg-slate-100/50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent dark:bg-slate-950 dark:border-slate-800"
            placeholder="e.g. Growth Core Equity"
            required
          />
        </div>

        {/* Dynamic Ticker Rows */}
        <div className="space-y-3">
          <div className="flex justify-between items-center text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 px-2">
            <span>Asset Ticker</span>
            <span className="w-24 text-right pr-6">Weight (%)</span>
          </div>

          <div className="space-y-2 max-h-[280px] overflow-y-auto pr-1">
            {rows.map((row, idx) => (
              <div
                key={idx}
                className="flex items-center space-x-2 bg-slate-100/30 dark:bg-slate-900/30 p-2 rounded-xl border border-slate-200/50 dark:border-slate-800/50 group hover:border-slate-300 dark:hover:border-slate-700 transition-colors duration-200"
              >
                <input
                  type="text"
                  value={row.ticker}
                  onChange={(e) => handleTickerChange(idx, e.target.value)}
                  className="flex-grow bg-transparent font-bold text-sm tracking-wider uppercase px-2 py-1.5 focus:outline-none"
                  placeholder="e.g. AAPL"
                  required
                />
                
                <div className="flex items-center space-x-2">
                  <input
                    type="number"
                    value={row.weight === 0 ? "" : row.weight}
                    onChange={(e) => handleWeightChange(idx, e.target.value)}
                    className="w-20 bg-slate-200/50 border border-slate-200/20 text-right rounded-lg px-2 py-1.5 font-bold text-sm focus:outline-none dark:bg-slate-950"
                    placeholder="0"
                    min="0"
                    max="100"
                    step="any"
                    required
                  />
                  <span className="text-slate-400 font-semibold text-sm">%</span>
                </div>

                <button
                  type="button"
                  onClick={() => removeRow(idx)}
                  className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-colors duration-200"
                  aria-label="Remove Ticker Row"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>

          <button
            type="button"
            onClick={addRow}
            className="w-full border-2 border-dashed border-slate-200 hover:border-sky-500/50 py-3 rounded-xl flex items-center justify-center gap-2 text-slate-500 hover:text-sky-500 text-sm font-semibold transition-all dark:border-slate-800 dark:hover:border-sky-500/30"
          >
            <Plus className="w-4 h-4" />
            Add Symbol Asset
          </button>
        </div>

        {/* Dynamic Weight Summary and Error Panel */}
        <div className="pt-4 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <span className="text-sm font-semibold text-slate-500 dark:text-slate-400">Total Allocation Weight:</span>
          <span
            className={`text-lg font-black tracking-tight ${
              Math.abs(totalWeight - 100) < 0.01
                ? "text-emerald-500"
                : "text-amber-500"
            }`}
          >
            {totalWeight.toFixed(1)}%
          </span>
        </div>

        {error && (
          <div className="bg-amber-500/10 border border-amber-500/20 text-amber-600 dark:text-amber-400 text-xs p-3.5 rounded-xl flex items-start gap-2.5">
            <ShieldAlert className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <p className="font-semibold">{error}</p>
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-gradient-to-r from-sky-600 to-emerald-600 hover:from-sky-500 hover:to-emerald-500 text-white font-bold py-3.5 px-6 rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-sky-500/10 transition-all active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none"
        >
          {isLoading ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Launching Agent Crew...
            </>
          ) : (
            <>
              <Sparkles className="w-4.5 h-4.5" />
              Trigger Agent Analysis
            </>
          )}
        </button>
      </form>
    </div>
  );
}
