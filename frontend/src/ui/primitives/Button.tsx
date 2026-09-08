import React from "react";
import { Pressable, ViewStyle, ActivityIndicator } from "react-native";
import { colors } from "../tokens/colors";
import { radii } from "../tokens/radii";
import { Text } from "./Text";

export interface ButtonProps {
  onPress?: () => void;
  children: React.ReactNode;
  variant?: "primary" | "secondary" | "outline" | "ghost" | "danger" | "highlight";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
  disabled?: boolean;
  icon?: React.ReactNode;
  fullWidth?: boolean;
  accessibilityLabel?: string;
  style?: ViewStyle;
}

export const Button: React.FC<ButtonProps> = ({
  onPress,
  children,
  variant = "primary",
  size = "md",
  isLoading = false,
  disabled = false,
  icon,
  fullWidth = false,
  accessibilityLabel,
  style,
}) => {
  const isDisabled = disabled || isLoading;

  const sizeStyles: Record<string, ViewStyle> = {
    sm: { paddingVertical: 8, paddingHorizontal: 12, minHeight: 36 },
    md: { paddingVertical: 12, paddingHorizontal: 18, minHeight: 44 },
    lg: { paddingVertical: 14, paddingHorizontal: 24, minHeight: 52 },
  };

  const getVariantStyle = (pressed: boolean): ViewStyle => {
    switch (variant) {
      case "primary":
        return {
          backgroundColor: pressed ? colors.accentHover : colors.accent,
          borderWidth: 1,
          borderColor: colors.accent,
        };
      case "secondary":
        return {
          backgroundColor: pressed ? colors.surfaceMuted : colors.surfaceSubtle,
          borderWidth: 1,
          borderColor: colors.border,
        };
      case "outline":
        return {
          backgroundColor: pressed ? colors.accentSubtle : "transparent",
          borderWidth: 1,
          borderColor: colors.accentBorder,
        };
      case "ghost":
        return {
          backgroundColor: pressed ? colors.surfaceSubtle : "transparent",
          borderWidth: 0,
        };
      case "danger":
        return {
          backgroundColor: colors.dangerSubtle,
          borderWidth: 1,
          borderColor: colors.danger,
        };
      case "highlight":
        return {
          backgroundColor: colors.highlight,
          borderWidth: 1,
          borderColor: colors.highlightBorder,
        };
      default:
        return { backgroundColor: colors.accent };
    }
  };

  return (
    <Pressable
      onPress={isDisabled ? undefined : onPress}
      accessibilityRole="button"
      accessibilityLabel={accessibilityLabel || (typeof children === "string" ? children : undefined)}
      accessibilityState={{ disabled: isDisabled, busy: isLoading }}
      style={({ pressed }) => ({
        flexDirection: "row",
        alignItems: "center",
        justifyContent: "center",
        borderRadius: radii.md,
        width: fullWidth ? "100%" : "auto",
        opacity: isDisabled ? 0.5 : pressed ? 0.85 : 1,
        ...sizeStyles[size],
        ...getVariantStyle(pressed),
        ...style,
      })}
    >
      {isLoading ? (
        <ActivityIndicator
          size="small"
          color={variant === "primary" || variant === "highlight" ? colors.textInverse : colors.accent}
          style={{ marginRight: 8 }}
        />
      ) : icon ? (
        <React.Fragment>{icon}</React.Fragment>
      ) : null}
      <Text
        variant={size === "sm" ? "sm" : size === "lg" ? "lg" : "base"}
        weight="semibold"
        color={
          variant === "primary" || variant === "highlight"
            ? "inverse"
            : variant === "danger"
            ? "danger"
            : variant === "outline"
            ? "accent"
            : "primary"
        }
      >
        {children}
      </Text>
    </Pressable>
  );
};
