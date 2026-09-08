import { createRequire } from "module";
const require = createRequire(import.meta.url);

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        background: "#f8fafc",
        surface: {
          DEFAULT: "#ffffff",
          subtle: "#f1f5f9",
          muted: "#e2e8f0",
          inverse: "#0f172a",
        },
        textPrimary: "#0f172a",
        textSecondary: "#64748b",
        textMuted: "#94a3b8",
        textInverse: "#ffffff",
        border: {
          DEFAULT: "#e2e8f0",
          dark: "#cbd5e1",
          focus: "#6366f1",
        },
        accent: {
          DEFAULT: "#6366f1",
          hover: "#4f46e5",
          subtle: "#eef2ff",
          border: "#c7d2fe",
        },
        highlight: {
          DEFAULT: "#9333ea",
          subtle: "#fdf4ff",
          border: "#f0abfc",
        },
        danger: {
          DEFAULT: "#dc2626",
          subtle: "#fef2f2",
        },
        success: {
          DEFAULT: "#16a34a",
          subtle: "#f0fdf4",
        },
        warning: {
          DEFAULT: "#d97706",
          subtle: "#fffbeb",
        },
      },
      borderRadius: {
        sm: "6px",
        md: "10px",
        lg: "16px",
        xl: "24px",
      },
    },
  },
  plugins: [],
};
