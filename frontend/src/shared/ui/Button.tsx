import React from "react";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "danger" | "brand";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
  icon?: React.ReactNode;
  fullWidth?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = "primary",
  size = "md",
  isLoading = false,
  icon,
  fullWidth = false,
  disabled,
  style,
  className = "",
  ...rest
}) => {
  const isDisabled = disabled || isLoading;

  const sizeStyles: Record<string, React.CSSProperties> = {
    sm: {
      padding: "0.4rem 0.75rem",
      fontSize: "0.825rem",
      minHeight: "36px",
      gap: "0.4rem",
    },
    md: {
      padding: "0.6rem 1.1rem",
      fontSize: "0.9rem",
      minHeight: "44px", // Touch-friendly minimum target
      gap: "0.5rem",
    },
    lg: {
      padding: "0.75rem 1.5rem",
      fontSize: "1rem",
      minHeight: "50px",
      gap: "0.6rem",
    },
  };

  const variantStyles: Record<string, React.CSSProperties> = {
    primary: {
      backgroundColor: "#1890ff",
      color: "#ffffff",
      border: "1px solid #1890ff",
    },
    brand: {
      backgroundColor: "#6366f1",
      color: "#ffffff",
      border: "1px solid #6366f1",
      boxShadow: "0 2px 4px rgba(99, 102, 241, 0.2)",
    },
    secondary: {
      backgroundColor: "#f1f5f9",
      color: "#334155",
      border: "1px solid #e2e8f0",
    },
    outline: {
      backgroundColor: "transparent",
      color: "#334155",
      border: "1px solid #cbd5e1",
    },
    ghost: {
      backgroundColor: "transparent",
      color: "#475569",
      border: "1px solid transparent",
    },
    danger: {
      backgroundColor: "#fff1f0",
      color: "#cf1322",
      border: "1px solid #ffa39e",
    },
  };

  const baseStyle: React.CSSProperties = {
    display: fullWidth ? "flex" : "inline-flex",
    width: fullWidth ? "100%" : "auto",
    alignItems: "center",
    justifyContent: "center",
    borderRadius: "8px",
    fontWeight: 600,
    cursor: isDisabled ? "not-allowed" : "pointer",
    opacity: isDisabled ? 0.65 : 1,
    transition: "all 0.15s ease-in-out",
    boxSizing: "border-box",
    textAlign: "center",
    textDecoration: "none",
    userSelect: "none",
    ...sizeStyles[size],
    ...variantStyles[variant],
    ...style,
  };

  return (
    <button
      style={baseStyle}
      disabled={isDisabled}
      className={`jester-btn ${className}`}
      {...rest}
    >
      {isLoading ? (
        <span style={{ display: "inline-block", animation: "spin 1s linear infinite" }}>⌛</span>
      ) : (
        icon && <span className="btn-icon">{icon}</span>
      )}
      <span>{children}</span>
    </button>
  );
};
