import React from "react";
import { Text as RNText, TextProps as RNTextProps, TextStyle } from "react-native";
import { colors } from "../tokens/colors";
import { typography } from "../tokens/typography";

export interface TextProps extends RNTextProps {
  variant?: keyof typeof typography.fontSize;
  weight?: keyof typeof typography.fontWeight;
  color?: "primary" | "secondary" | "muted" | "inverse" | "accent" | "danger" | "success" | "highlight" | "warning";
  align?: "left" | "center" | "right";
  style?: TextStyle;
  children?: React.ReactNode;
}

export const Text: React.FC<TextProps> = ({
  variant = "base",
  weight = "normal",
  color = "primary",
  align,
  style,
  children,
  ...props
}) => {
  const colorMap: Record<string, string> = {
    primary: colors.textPrimary,
    secondary: colors.textSecondary,
    muted: colors.textMuted,
    inverse: colors.textInverse,
    accent: colors.accent,
    danger: colors.danger,
    success: colors.success,
    highlight: colors.highlight,
    warning: colors.warning,
  };

  const computedStyle: TextStyle = {
    fontSize: typography.fontSize[variant],
    fontWeight: typography.fontWeight[weight],
    color: colorMap[color] || colors.textPrimary,
    fontFamily: typography.fontFamily.sans,
    ...(align ? { textAlign: align } : {}),
    ...style,
  };

  return (
    <RNText style={computedStyle} {...props}>
      {children}
    </RNText>
  );
};
