import React, { useState } from "react";
import { View, TextInput, TextInputProps, ViewStyle, TextStyle } from "react-native";
import { colors } from "../tokens/colors";
import { radii } from "../tokens/radii";
import { typography } from "../tokens/typography";
import { Text } from "./Text";

export interface InputProps extends TextInputProps {
  label?: string;
  error?: string;
  helperText?: string;
  containerStyle?: ViewStyle;
  inputStyle?: TextStyle;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  helperText,
  containerStyle,
  inputStyle,
  onFocus,
  onBlur,
  ...props
}) => {
  const [isFocused, setIsFocused] = useState(false);

  return (
    <View style={[{ width: "100%", marginBottom: 12 }, containerStyle]}>
      {label && (
        <Text
          variant="sm"
          weight="semibold"
          color="secondary"
          style={{ marginBottom: 6 }}
        >
          {label}
        </Text>
      )}

      <TextInput
        onFocus={(e) => {
          setIsFocused(true);
          onFocus?.(e);
        }}
        onBlur={(e) => {
          setIsFocused(false);
          onBlur?.(e);
        }}
        placeholderTextColor={colors.textMuted}
        style={[
          {
            backgroundColor: colors.surface,
            borderWidth: 1,
            borderColor: error
              ? colors.danger
              : isFocused
              ? colors.borderFocus
              : colors.border,
            borderRadius: radii.md,
            paddingHorizontal: 14,
            paddingVertical: 10,
            fontSize: typography.fontSize.base,
            color: colors.textPrimary,
            fontFamily: typography.fontFamily.sans,
            minHeight: 44,
          },
          inputStyle,
        ]}
        {...props}
      />

      {error ? (
        <Text variant="xs" color="danger" style={{ marginTop: 4 }}>
          {error}
        </Text>
      ) : helperText ? (
        <Text variant="xs" color="muted" style={{ marginTop: 4 }}>
          {helperText}
        </Text>
      ) : null}
    </View>
  );
};
