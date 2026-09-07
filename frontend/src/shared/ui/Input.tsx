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
  ...rest
}) => {
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
            fontWeight: 600,
            color: "#1e293b",
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
          backgroundColor: disabled ? "#f8fafc" : "#ffffff",
          border: `1px solid ${error ? "#ef4444" : "#cbd5e1"}`,
          borderRadius: "8px",
          padding: "0 0.75rem",
          minHeight: "44px", // Touch target height
          transition: "border-color 0.15s ease",
          boxSizing: "border-box",
        }}
      >
        {prefixIcon && (
          <span style={{ marginRight: "0.5rem", color: "#64748b", display: "flex" }}>
            {prefixIcon}
          </span>
        )}

        <input
          id={inputId}
          disabled={disabled}
          style={{
            flex: 1,
            border: "none",
            outline: "none",
            background: "transparent",
            fontSize: "0.95rem",
            color: "#0f172a",
            padding: "0.5rem 0",
            minWidth: 0,
            ...style,
          }}
          {...rest}
        />

        {suffixIcon && (
          <span style={{ marginLeft: "0.5rem", color: "#64748b", display: "flex" }}>
            {suffixIcon}
          </span>
        )}
      </div>

      {error ? (
        <span style={{ fontSize: "0.8rem", color: "#ef4444", marginTop: "0.25rem" }}>
          {error}
        </span>
      ) : helperText ? (
        <span style={{ fontSize: "0.8rem", color: "#64748b", marginTop: "0.25rem" }}>
          {helperText}
        </span>
      ) : null}
    </div>
  );
};
