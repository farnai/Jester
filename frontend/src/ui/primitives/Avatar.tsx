import React from "react";
import { View, Image, ViewStyle } from "react-native";
import { colors } from "../tokens/colors";
import { radii } from "../tokens/radii";
import { Text } from "./Text";

export interface AvatarProps {
  src?: string | null;
  name?: string | null;
  size?: "sm" | "md" | "lg" | "xl";
  isOnline?: boolean;
  style?: ViewStyle;
}

export const Avatar: React.FC<AvatarProps> = ({
  src,
  name,
  size = "md",
  isOnline,
  style,
}) => {
  const sizeMap = {
    sm: 32,
    md: 44,
    lg: 56,
    xl: 72,
  };

  const dim = sizeMap[size];

  const getInitials = (text?: string | null) => {
    if (!text) return "🃏";
    const parts = text.trim().split(" ");
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return text.substring(0, 2).toUpperCase();
  };

  return (
    <View style={[{ width: dim, height: dim, position: "relative" }, style]}>
      <View
        style={{
          width: dim,
          height: dim,
          borderRadius: radii.full,
          backgroundColor: colors.accentSubtle,
          borderWidth: 1,
          borderColor: colors.accentBorder,
          alignItems: "center",
          justifyContent: "center",
          overflow: "hidden",
        }}
      >
        {src ? (
          <Image
            source={{ uri: src }}
            style={{ width: dim, height: dim }}
            resizeMode="cover"
          />
        ) : (
          <Text
            variant={size === "sm" ? "xs" : size === "xl" ? "xl" : "base"}
            weight="bold"
            color="accent"
          >
            {getInitials(name)}
          </Text>
        )}
      </View>

      {isOnline !== undefined && (
        <View
          style={{
            position: "absolute",
            bottom: 0,
            right: 0,
            width: Math.max(10, dim * 0.25),
            height: Math.max(10, dim * 0.25),
            borderRadius: radii.full,
            backgroundColor: isOnline ? colors.success : colors.textMuted,
            borderWidth: 2,
            borderColor: colors.surface,
          }}
        />
      )}
    </View>
  );
};
