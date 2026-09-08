import React from "react";
import { View, ViewStyle } from "react-native";
import { colors } from "../tokens/colors";
import { radii } from "../tokens/radii";
import { Text } from "./Text";

export interface BadgeProps {
  children: React.ReactNode;
  variant?: "brand" | "highlight" | "neutral" | "success" | "danger" | "warning";
  size?: "sm" | "md";
  style?: ViewStyle;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = "brand",
  size = "md",
  style,
}) => {
  const variantStyles: Record<string, { bg: string; border: string; textColor: "accent" | "highlight" | "secondary" | "success" | "danger" | "warning" }> = {
    brand: { bg: colors.accentSubtle, border: colors.accentBorder, textColor: "accent" },
    highlight: { bg: colors.highlightSubtle, border: colors.highlightBorder, textColor: "highlight" },
    neutral: { bg: colors.surfaceSubtle, border: colors.border, textColor: "secondary" },
    success: { bg: colors.successSubtle, border: colors.success, textColor: "success" },
    danger: { bg: colors.dangerSubtle, border: colors.danger, textColor: "danger" },
    warning: { bg: colors.warningSubtle, border: colors.warning, textColor: "warning" },
  };

  const current = variantStyles[variant] || variantStyles.brand;

  return (
    <View
      style={{
        flexDirection: "row",
        alignItems: "center",
        alignSelf: "flex-start",
        backgroundColor: current.bg,
        borderColor: current.border,
        borderWidth: 1,
        borderRadius: radii.full,
        paddingHorizontal: size === "sm" ? 8 : 10,
        paddingVertical: size === "sm" ? 2 : 4,
        ...style,
      }}
    >
      <Text variant={size === "sm" ? "xs" : "sm"} weight="semibold" color={current.textColor}>
        {children}
      </Text>
    </View>
  );
};
