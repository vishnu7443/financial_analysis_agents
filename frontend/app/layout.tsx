"use client";

import { useEffect, useState } from "react";
import "./globals.css";
import { Sun, Moon, AreaChart, Cpu, Terminal } from "lucide-react";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [darkMode, setDarkMode] = useState(true);

  useEffect(() => {
    // Default to dark mode for elite terminal aesthetics
    const root = window.document.documentElement;
    if (darkMode) {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
  }, [darkMode]);

  return (
    <html lang="en" className="dark">
      <head>
        <title>Portfolio Analyst Crew - Multi-Agent Dashboard</title>
        <meta name="description" content="AI Agent Crew providing deterministic real-time market risk, VADER news sentiments, and Claude streams." />
        <link rel="icon" href="/favicon.ico" />
      </head>
      <body className="bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-50 transition-colors duration-300 antialiased relative min-h-screen">
        {/* Decorative background grid and blurs */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:14px_24px] pointer-events-none z-0" />
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-sky-500/10 rounded-full blur-[120px] pointer-events-none z-0 dark:bg-sky-500/5" />
        <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-emerald-500/10 rounded-full blur-[120px] pointer-events-none z-0 dark:bg-emerald-500/5" />

        <div className="relative z-10 flex flex-col min-h-screen">
          {/* Header Navigation */}
          <header className="border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
              <a href="/" className="flex items-center space-x-3 group">
                <div className="p-2 bg-gradient-to-tr from-sky-500 to-emerald-500 rounded-xl text-white shadow-md shadow-sky-500/20 group-hover:scale-105 transition-transform duration-200">
                  <AreaChart className="h-5 w-5" />
                </div>
                <div>
                  <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-sky-600 to-emerald-500 bg-clip-text text-transparent dark:from-sky-400 dark:to-emerald-400">
                    ANTIGRAVITY
                  </span>
                  <span className="text-xs font-semibold uppercase tracking-widest text-slate-400 block -mt-1 dark:text-slate-500">
                    AI AGENT OPS
                  </span>
                </div>
              </a>

              <nav className="flex items-center space-x-4">
                {/* Active compliance status */}
                <div className="hidden sm:flex items-center space-x-2 bg-emerald-500/10 text-emerald-600 px-3 py-1 rounded-full text-xs font-semibold border border-emerald-500/20 dark:text-emerald-400">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                  <span>Agent Engine: Online</span>
                </div>

                {/* Dark Mode toggle */}
                <button
                  onClick={() => setDarkMode(!darkMode)}
                  className="p-2 rounded-xl border border-slate-200 hover:bg-slate-100 text-slate-600 transition-all dark:border-slate-800 dark:hover:bg-slate-800 dark:text-slate-400"
                  aria-label="Toggle Theme Mode"
                  id="theme-toggle-btn"
                >
                  {darkMode ? <Sun className="h-4.5 w-4.5" /> : <Moon className="h-4.5 w-4.5" />}
                </button>
              </nav>
            </div>
          </header>

          {/* Main page content container */}
          <main className="flex-grow max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 relative">
            {children}
          </main>

          {/* Premium Footer */}
          <footer className="border-t border-slate-200 dark:border-slate-800 py-6 text-center text-xs text-slate-400 dark:text-slate-600 bg-white/40 dark:bg-slate-950/40">
            <p>
              &copy; 2026 Antigravity AI Operations. Built on explicit Think &rarr; Decide &rarr; Act Reasoning Logs.
            </p>
          </footer>
        </div>
      </body>
    </html>
  );
}
