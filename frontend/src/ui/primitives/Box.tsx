import React from "react";
import { View, ViewProps, ViewStyle } from "react-native";
import { colors } from "../tokens/colors";
import { radii } from "../tokens/radii";

export interface BoxProps extends ViewProps {
  surface?: "default" | "subtle" | "muted" | "inverse" | "transparent";
  rounded?: keyof typeof radii;
  padding?: number;
  style?: ViewStyle;
  children?: React.ReactNode;
}

export const Box: React.FC<BoxProps> = ({
  surface = "transparent",
  rounded,
  padding,
  style,
  children,
  ...props
}) => {
  const surfaceStyles: Record<string, ViewStyle> = {
    default: { backgroundColor: colors.surface },
    subtle: { backgroundColor: colors.surfaceSubtle },
    muted: { backgroundColor: colors.surfaceMuted },
    inverse: { backgroundColor: colors.surfaceInverse },
    transparent: { backgroundColor: "transparent" },
  };

  const computedStyle: ViewStyle = {
    ...surfaceStyles[surface],
    ...(rounded ? { borderRadius: radii[rounded] } : {}),
    ...(padding !== undefined ? { padding } : {}),
    ...style,
  };

  return (
    <View style={computedStyle} {...props}>
      {children}
    </View>
  );
};
