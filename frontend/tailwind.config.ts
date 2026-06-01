import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class", // Enables premium class-based dark mode
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        border: "var(--border)",
        card: "var(--card)",
        primary: {
          50: "#f0f9ff",
          100: "#e0f2fe",
          500: "#0284c7",
          600: "#025a9c",
          900: "#0c4a6e"
        },
        slate: {
          900: "#0f172a",
          950: "#020617"
        }
      },
      animation: {
        "fade-in-up": "fadeInUp 0.6s ease-out forwards",
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "shimmer": "shimmer 2.5s infinite linear",
        "terminal-glow": "terminalGlow 1.5s ease-in-out infinite alternate"
      },
      keyframes: {
        fadeInUp: {
          "0%": { opacity: "0", transform: "translateY(15px)" },
          "100%": { opacity: "1", transform: "translateY(0)" }
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0%" },
          "100%": { backgroundPosition: "200% 0%" }
        },
        terminalGlow: {
          "0%": { boxShadow: "0 0 4px rgba(34, 197, 94, 0.2)" },
          "100%": { boxShadow: "0 0 12px rgba(34, 197, 94, 0.6)" }
        }
      }
    },
  },
  plugins: [],
};
export default config;
