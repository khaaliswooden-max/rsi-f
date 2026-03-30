import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Palantir Blueprint dark palette
        bp: {
          dark1: "#252a31",
          dark2: "#1c2127",
          dark3: "#111418",
          dark4: "#0d1117",
          border: "#383e47",
          "border-muted": "#2f343c",
          text: "#f6f7f9",
          "text-secondary": "#abb3bf",
          "text-muted": "#738091",
          "text-disabled": "#5f6b7c",
          // Intent colors
          blue: "#4c90f0",
          "blue-dim": "#2d72d2",
          "blue-dark": "#215db0",
          "blue-bg": "rgba(76, 144, 240, 0.15)",
          green: "#32a467",
          "green-dim": "#238551",
          "green-dark": "#1c7346",
          "green-bg": "rgba(50, 164, 103, 0.15)",
          orange: "#c87619",
          "orange-dim": "#935610",
          "orange-bg": "rgba(200, 118, 25, 0.15)",
          red: "#e76a6e",
          "red-dim": "#cd4246",
          "red-dark": "#ac2f33",
          "red-bg": "rgba(231, 106, 110, 0.15)",
          // Highlight / selection
          highlight: "rgba(76, 144, 240, 0.2)",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
        mono: ["'JetBrains Mono'", "'Fira Code'", "Consolas", "monospace"],
      },
      fontSize: {
        "2xs": ["0.65rem", { lineHeight: "1rem" }],
      },
      boxShadow: {
        "bp-md": "0 2px 8px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.04)",
        "bp-lg": "0 8px 24px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.04)",
        "bp-inset": "inset 0 1px 3px rgba(0,0,0,0.4)",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
    },
  },
  plugins: [],
};

export default config;
