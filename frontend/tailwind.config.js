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
        background: "#FAF7F2",
        surface: {
          DEFAULT: "#FFFFFF",
          base: "#FFFDFA",
          subtle: "#F3EEE6",
          muted: "#E6E0D7",
          inverse: "#222630",
        },
        textPrimary: "#222630",
        textSecondary: "#6A716F",
        textMuted: "#8B918F",
        textInverse: "#FFFFFF",
        border: {
          DEFAULT: "#E6E0D7",
          muted: "#D8D1C7",
          interactive: "#8F8A83",
          dark: "#D8D1C7",
          focus: "#9E4215",
        },
        accent: {
          DEFAULT: "#FF7A2F",
          hover: "#E9681F",
          pressed: "#C95618",
          subtle: "#FFE7D7",
          border: "#FFB185",
          dark: "#9E4215",
          label: "#222630",
        },
        highlight: {
          DEFAULT: "#FF7A2F",
          subtle: "#FBEEE7",
          border: "#F5DDD1",
        },
        brand: {
          50: "#FFF6F0",
          100: "#FFE7D7",
          200: "#FFD0B2",
          300: "#FFB185",
          400: "#FF925A",
          500: "#FF7A2F",
          600: "#E9681F",
          700: "#C95618",
          800: "#9E4215",
          900: "#713111",
        },
        sage: {
          50: "#F4F8F1",
          100: "#E8EFE2",
          200: "#D6E1CD",
          300: "#BACAAC",
          400: "#95A686",
          500: "#788A69",
          ink: "#4B6242",
        },
        peach: {
          DEFAULT: "#F5DDD1",
          soft: "#FBEEE7",
        },
        danger: {
          DEFAULT: "#AE3534",
          subtle: "#FBE9E8",
        },
        success: {
          DEFAULT: "#4B6242",
          subtle: "#EAF4EA",
        },
        warning: {
          DEFAULT: "#925C18",
          subtle: "#FFF3DE",
        },
        info: {
          DEFAULT: "#396F87",
          subtle: "#EAF1F7",
        },
      },
      borderRadius: {
        sm: "6px",
        md: "10px",
        lg: "16px",
        xl: "24px",
      },
      fontFamily: {
        sans: ['"Noto Sans Georgian"', 'system-ui', '-apple-system', 'sans-serif'],
        serif: ['Georgia', 'serif'],
      },
    },
  },
  plugins: [],
};
