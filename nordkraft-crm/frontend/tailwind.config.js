/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        nk: {
          bg:       "#0a0b0d",
          surface:  "#111317",
          surface2: "#181b20",
          border:   "#ffffff14",
          border2:  "#ffffff22",
          text:     "#f0f2f5",
          muted:    "#8892a0",
          accent:   "#3b7ff5",
          green:    "#00c98d",
          warn:     "#f5a623",
          danger:   "#e84040",
          purple:   "#a855f7",
        },
      },
      fontFamily: {
        sans: ["'SF Pro Display'", "system-ui", "-apple-system", "sans-serif"],
        mono: ["'SF Mono'", "monospace"],
      },
      borderWidth: {
        "0.5": "0.5px",
      },
    },
  },
  plugins: [],
};
