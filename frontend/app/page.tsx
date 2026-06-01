"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import PortfolioInput from "@/components/PortfolioInput";
import { Cpu, AreaChart, Layers, HelpCircle, ArrowRight } from "lucide-react";

export default function HomePage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handlePortfolioSubmit = async (portfolio: { name: string; tickers: { ticker: string; weight: number }[] }) => {
    setIsLoading(true);
    setError(null);
    try {
      logger_log("API: Posting portfolio to backend...");
      const response = await fetch("http://localhost:8000/api/portfolio", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(portfolio),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to submit portfolio allocations.");
      }

      const data = await response.json();
      logger_log(`API: Portfolio saved. Dispatched Job ID: ${data.job_id}`);
      
      // Redirect to the live tracking session
      router.push(`/dashboard/${data.job_id}`);
    } catch (e: any) {
      setError(e.message || "Unable to contact the backend agent server. Please make sure the FastAPI server is running on port 8000.");
      setIsLoading(false);
    }
  };

  // Helper logger
  const logger_log = (msg: string) => {
    console.log(`[Platform] ${msg}`);
  };

  return (
    <div className="space-y-12 max-w-5xl mx-auto py-6 animate-fade-in-up">
      {/* 1. Brand Hero Pitch */}
      <div className="text-center space-y-4 max-w-3xl mx-auto">
        <div className="inline-flex items-center gap-1.5 bg-gradient-to-r from-sky-500/10 to-emerald-500/10 border border-sky-500/20 text-sky-600 px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-widest dark:text-sky-400">
          <Cpu className="w-3.5 h-3.5 animate-spin-slow" />
          LangGraph Multi-Agent Orchestration
        </div>
        
        <h1 className="text-4xl md:text-5xl font-black tracking-tight leading-tight select-none">
          Autonomous Portfolio Risk &amp; <br />
          <span className="bg-gradient-to-r from-sky-500 via-sky-600 to-emerald-500 bg-clip-text text-transparent dark:from-sky-400 dark:to-emerald-400">
            Sentiment Agent Intelligence
          </span>
        </h1>
        
        <p className="text-sm md:text-base text-slate-500 dark:text-slate-400 leading-relaxed max-w-2xl mx-auto">
          Deploy an autonomous crew of expert AI agents. Our Market, Sentiment, and Writing agents cooperate in parallel under a deterministic Think-Decide-Act loop to stress-test assets, scan narratives, and compile streaming investment briefs.
        </p>
      </div>

      {/* 2. Main Portfolio Configuration and Explainer Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Side: Features breakdown list (4 cols) */}
        <div className="lg:col-span-5 space-y-6 lg:sticky lg:top-24">
          <h3 className="font-extrabold text-lg text-slate-900 dark:text-slate-50 uppercase tracking-wider">
            Agent Crew Breakdown
          </h3>
          
          <div className="space-y-4">
            {/* Feature 1 */}
            <div className="flex items-start gap-4">
              <div className="p-2.5 bg-sky-500/10 text-sky-600 rounded-xl dark:bg-sky-500/5 dark:text-sky-400 border border-sky-500/10">
                <AreaChart className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold text-sm text-slate-800 dark:text-slate-200">1. Market Metrics Scan</h4>
                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed mt-0.5">
                  Gathers current prices, trailing valuation ratios, beta coefficients, and 1-year historical prices from Yahoo Finance with robust local caching.
                </p>
              </div>
            </div>

            {/* Feature 2 */}
            <div className="flex items-start gap-4">
              <div className="p-2.5 bg-emerald-500/10 text-emerald-600 rounded-xl dark:bg-emerald-500/5 dark:text-emerald-400 border border-emerald-500/10">
                <Layers className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold text-sm text-slate-800 dark:text-slate-200">2. Social Narrative Audit</h4>
                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed mt-0.5">
                  Audits financial news headlines using NewsAPI and scores qualitative market consensus utilizing VADER Sentiment analysis.
                </p>
              </div>
            </div>

            {/* Feature 3 */}
            <div className="flex items-start gap-4">
              <div className="p-2.5 bg-purple-500/10 text-purple-600 rounded-xl dark:bg-purple-500/5 dark:text-purple-400 border border-purple-500/10">
                <Cpu className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold text-sm text-slate-800 dark:text-slate-200">3. Deterministic LangGraph execution</h4>
                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed mt-0.5">
                  Coordinates nodes in parallel, calculates weighted-beta risk factors, and streams markdown investment reviews from Claude token-by-token.
                </p>
              </div>
            </div>
          </div>

          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 text-xs rounded-xl flex items-start gap-2.5 leading-relaxed font-semibold">
              <HelpCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <div>
                <p className="font-bold">Database / Connection Timeout</p>
                <p className="mt-0.5 font-medium">{error}</p>
              </div>
            </div>
          )}
        </div>

        {/* Right Side: Portfolio Input Form (7 cols) */}
        <div className="lg:col-span-7">
          <PortfolioInput onSubmit={handlePortfolioSubmit} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
}
