import React from "react";
import { View, ViewStyle, ViewProps } from "react-native";
import { colors } from "../tokens/colors";
import { radii } from "../tokens/radii";
import { shadows } from "../tokens/shadows";

export interface CardProps extends ViewProps {
  elevation?: "none" | "sm" | "md" | "lg";
  variant?: "surface" | "subtle" | "highlight" | "bordered";
  padding?: number;
  rounded?: keyof typeof radii;
  style?: ViewStyle;
  children?: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({
  elevation = "sm",
  variant = "surface",
  padding = 16,
  rounded = "lg",
  style,
  children,
  ...props
}) => {
  const variantStyles: Record<string, ViewStyle> = {
    surface: {
      backgroundColor: colors.surface,
      borderColor: colors.border,
      borderWidth: 1,
    },
    subtle: {
      backgroundColor: colors.surfaceSubtle,
      borderColor: colors.border,
      borderWidth: 1,
    },
    highlight: {
      backgroundColor: colors.highlightSubtle,
      borderColor: colors.highlightBorder,
      borderWidth: 1,
    },
    bordered: {
      backgroundColor: colors.surface,
      borderColor: colors.accentBorder,
      borderWidth: 1.5,
    },
  };

  return (
    <View
      style={{
        borderRadius: radii[rounded],
        padding,
        ...variantStyles[variant],
        ...shadows[elevation],
        ...style,
      }}
      {...props}
    >
      {children}
    </View>
  );
};
