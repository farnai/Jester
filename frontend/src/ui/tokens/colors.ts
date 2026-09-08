export const colors = {
  background: "#f8fafc",
  surface: "#ffffff",
  surfaceSubtle: "#f1f5f9",
  surfaceMuted: "#e2e8f0",
  surfaceInverse: "#0f172a",

  textPrimary: "#0f172a",
  textSecondary: "#64748b",
  textMuted: "#94a3b8",
  textInverse: "#ffffff",

  border: "#e2e8f0",
  borderDark: "#cbd5e1",
  borderFocus: "#6366f1",

  accent: "#6366f1",
  accentHover: "#4f46e5",
  accentSubtle: "#eef2ff",
  accentBorder: "#c7d2fe",

  highlight: "#9333ea",
  highlightSubtle: "#fdf4ff",
  highlightBorder: "#f0abfc",

  success: "#16a34a",
  successSubtle: "#f0fdf4",
  warning: "#d97706",
  warningSubtle: "#fffbeb",
  danger: "#dc2626",
  dangerSubtle: "#fef2f2",
  info: "#2563eb",
  infoSubtle: "#eff6ff",
} as const;

export type ColorToken = keyof typeof colors;
