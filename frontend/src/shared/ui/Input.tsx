import React from "react";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  helperText?: string;
  error?: string | null;
  prefixIcon?: React.ReactNode;
  suffixIcon?: React.ReactNode;
  fullWidth?: boolean;
}

export const Input: React.FC<InputProps> = ({
  label,
  helperText,
  error,
  prefixIcon,
  suffixIcon,
  fullWidth = true,
  disabled,
  style,
  id,
  onFocus,
  onBlur,
  ...rest
}) => {
  const [isFocused, setIsFocused] = React.useState(false);
  const inputId = id || (label ? `input-${label.toLowerCase().replace(/\s+/g, "-")}` : undefined);

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        width: fullWidth ? "100%" : "auto",
        marginBottom: "0.85rem",
      }}
    >
      {label && (
        <label
          htmlFor={inputId}
          style={{
            fontSize: "0.85rem",
            fontWeight: 700,
            color: "var(--jester-color-text-primary)",
            marginBottom: "0.35rem",
            display: "block",
          }}
        >
          {label}
        </label>
      )}

      <div
        style={{
          display: "flex",
          alignItems: "center",
          backgroundColor: disabled ? "var(--jester-color-surface-disabled)" : "var(--jester-color-surface)",
          // 3:1+ WCAG non-text contrast for interactive inputs (#8F8A83), focused (#9E4215), error (#AE3534)
          border: `1.5px solid ${error ? "var(--jester-color-danger-text)" : isFocused ? "var(--jester-color-brand-dark)" : "var(--jester-color-border-interactive)"}`,
          boxShadow: isFocused && !error ? "var(--jester-shadow-focus-ring)" : undefined,
          borderRadius: "10px",
          padding: "0 0.85rem",
          minHeight: "44px", // Accessible 44px touch target height
          transition: "border-color 0.15s ease, box-shadow 0.15s ease",
          boxSizing: "border-box",
        }}
      >
        {prefixIcon && (
          <span style={{ marginRight: "0.5rem", color: "var(--jester-color-text-secondary)", display: "flex" }}>
            {prefixIcon}
          </span>
        )}

        <input
          id={inputId}
          disabled={disabled}
          onFocus={(e) => {
            setIsFocused(true);
            onFocus?.(e);
          }}
          onBlur={(e) => {
            setIsFocused(false);
            onBlur?.(e);
          }}
          style={{
            flex: 1,
            border: "none",
            outline: "none",
            background: "transparent",
            fontSize: "0.95rem",
            color: "var(--jester-color-text-primary)",
            padding: "0.6rem 0",
            minWidth: 0,
            ...style,
          }}
          {...rest}
        />

        {suffixIcon && (
          <span style={{ marginLeft: "0.5rem", color: "var(--jester-color-text-secondary)", display: "flex" }}>
            {suffixIcon}
          </span>
        )}
      </div>

      {error ? (
        <span style={{ fontSize: "0.8rem", color: "var(--jester-color-danger-text)", marginTop: "0.3rem", fontWeight: 600 }}>
          {error}
        </span>
      ) : helperText ? (
        <span style={{ fontSize: "0.8rem", color: "var(--jester-color-text-secondary)", marginTop: "0.25rem" }}>
          {helperText}
        </span>
      ) : null}
    </div>
  );
};
