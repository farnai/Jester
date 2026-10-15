/**
 * JESTER Design System v1 — Color Tokens
 * Founder-selected palette (2026-10-15)
 * Primary Accent: Vivid Clean Carrot Orange (#FF7A2F)
 * Surfaces: Warm pale paper tones (#FAF7F2, #F3EEE6)
 * Text: Deep charcoal (#222630), editorial slate (#6A716F)
 * Support: Measured Sage (#788A69, #4B6242) & Soft Peach (#FBEEE7)
 */

export const palette = {
  brand: {
    orange50: "#FFF6F0",
    orange100: "#FFE7D7",
    orange200: "#FFD0B2",
    orange300: "#FFB185",
    orange400: "#FF925A",
    orange500: "#FF7A2F", // Main Primary Brand Accent
    orange600: "#E9681F", // Hover
    orange700: "#C95618", // Pressed / Active
    orange800: "#9E4215", // Focus ring & Dark-orange white-label variant
    orange900: "#713111",
  },
  surface: {
    canvas: "#FAF7F2", // Main background
    base: "#FFFDFA",
    card: "#FFFFFF",
    alt: "#F3EEE6", // Subtle section surface
    raised: "#FFFFFF",
  },
  text: {
    primary: "#222630", // Deep charcoal (5.82:1 on #FF7A2F)
    secondary: "#6A716F", // Neutral slate
    tertiaryDecorative: "#8B918F",
    inverse: "#FFFFFF",
  },
  support: {
    sage50: "#F4F8F1",
    sage100: "#E8EFE2", // Soft calm insight background
    sage200: "#D6E1CD",
    sage300: "#BACAAC",
    sage400: "#95A686",
    sage500: "#788A69",
    sageInk: "#4B6242", // High contrast text on sage surfaces
  },
  accent: {
    peach: "#F5DDD1",
    peachSoft: "#FBEEE7", // Warm insight card background
  },
  border: {
    soft: "#E6E0D7", // Default divider & boundary
    muted: "#D8D1C7",
    interactive: "#8F8A83", // 3:1+ WCAG non-text contrast for inputs
  },
  semantic: {
    success: "#4B6242",
    successSoft: "#EAF4EA",
    warning: "#925C18",
    warningSoft: "#FFF3DE",
    error: "#AE3534",
    errorSoft: "#FBE9E8",
    info: "#396F87",
    infoSoft: "#EAF1F7",
  },
} as const;

export const colors = {
  // Foundations & Surfaces
  background: palette.surface.canvas, // #FAF7F2
  surface: palette.surface.card, // #FFFFFF
  surfaceSubtle: palette.surface.alt, // #F3EEE6
  surfaceMuted: palette.border.soft, // #E6E0D7
  surfaceInverse: palette.text.primary, // #222630

  // Typography Tones
  textPrimary: palette.text.primary, // #222630
  textSecondary: palette.text.secondary, // #6A716F
  textMuted: palette.text.tertiaryDecorative, // #8B918F
  textInverse: palette.text.inverse, // #FFFFFF

  // Borders
  border: palette.border.soft, // #E6E0D7
  borderDark: palette.border.muted, // #D8D1C7
  borderInteractive: palette.border.interactive, // #8F8A83
  borderFocus: palette.brand.orange800, // #9E4215

  // Primary Action (Carrot Orange)
  accent: palette.brand.orange500, // #FF7A2F
  accentHover: palette.brand.orange600, // #E9681F
  accentPressed: palette.brand.orange700, // #C95618
  accentSubtle: palette.brand.orange100, // #FFE7D7
  accentBorder: palette.brand.orange300, // #FFB185
  accentDark: palette.brand.orange800, // #9E4215 (For White label variant: 6.47:1)

  // Primary Button Label Contrast (CRITICAL: 5.82:1 with #FF7A2F)
  actionPrimaryLabel: palette.text.primary, // #222630
  actionPrimaryDarkLabel: palette.text.inverse, // #FFFFFF

  // Signature Jester Insight Highlights (Warm Peach & Soft Sage)
  highlight: palette.brand.orange500, // #FF7A2F
  highlightSubtle: palette.accent.peachSoft, // #FBEEE7
  highlightBorder: palette.accent.peach, // #F5DDD1

  // Supportive Sage Tones
  supportSage: palette.support.sage500, // #788A69
  supportSageSoft: palette.support.sage100, // #E8EFE2
  supportSageInk: palette.support.sageInk, // #4B6242

  // Semantic Feedback (Meaning-oriented)
  success: palette.semantic.success, // #4B6242
  successSubtle: palette.semantic.successSoft, // #EAF4EA
  warning: palette.semantic.warning, // #925C18
  warningSubtle: palette.semantic.warningSoft, // #FFF3DE
  danger: palette.semantic.error, // #AE3534
  dangerSubtle: palette.semantic.errorSoft, // #FBE9E8
  info: palette.semantic.info, // #396F87
  infoSubtle: palette.semantic.infoSoft, // #EAF1F7
} as const;

export type ColorToken = keyof typeof colors;

