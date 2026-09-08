import React from "react";
import { View, ViewStyle } from "react-native";
import { colors } from "../tokens/colors";

export interface DividerProps {
  orientation?: "horizontal" | "vertical";
  color?: string;
  thickness?: number;
  spacing?: number;
  style?: ViewStyle;
}

export const Divider: React.FC<DividerProps> = ({
  orientation = "horizontal",
  color = colors.border,
  thickness = 1,
  spacing = 12,
  style,
}) => {
  if (orientation === "vertical") {
    return (
      <View
        style={{
          width: thickness,
          backgroundColor: color,
          marginHorizontal: spacing,
          height: "100%",
          ...style,
        }}
      />
    );
  }

  return (
    <View
      style={{
        height: thickness,
        backgroundColor: color,
        marginVertical: spacing,
        width: "100%",
        ...style,
      }}
    />
  );
};
