import React from "react";
import { Pressable, ViewStyle } from "react-native";
import { colors } from "../tokens/colors";
import { radii } from "../tokens/radii";

export interface IconButtonProps {
  onPress?: () => void;
  icon: React.ReactNode;
  accessibilityLabel: string;
  size?: "sm" | "md" | "lg";
  variant?: "default" | "subtle" | "outline" | "danger";
  disabled?: boolean;
  style?: ViewStyle;
}

export const IconButton: React.FC<IconButtonProps> = ({
  onPress,
  icon,
  accessibilityLabel,
  size = "md",
  variant = "subtle",
  disabled = false,
  style,
}) => {
  const sizeMap = {
    sm: 36,
    md: 44,
    lg: 52,
  };

  const dim = sizeMap[size];

  const variantStyles: Record<string, ViewStyle> = {
    default: { backgroundColor: colors.accent, borderColor: colors.accent, borderWidth: 1 },
    subtle: { backgroundColor: colors.surfaceSubtle, borderColor: colors.border, borderWidth: 1 },
    outline: { backgroundColor: "transparent", borderColor: colors.borderDark, borderWidth: 1 },
    danger: { backgroundColor: colors.dangerSubtle, borderColor: colors.danger, borderWidth: 1 },
  };

  return (
    <Pressable
      onPress={disabled ? undefined : onPress}
      accessibilityRole="button"
      accessibilityLabel={accessibilityLabel}
      accessibilityState={{ disabled }}
      style={({ pressed }) => ({
        width: dim,
        height: dim,
        borderRadius: radii.full,
        alignItems: "center",
        justifyContent: "center",
        opacity: disabled ? 0.4 : pressed ? 0.75 : 1,
        ...variantStyles[variant],
        ...style,
      })}
    >
      {icon}
    </Pressable>
  );
};
