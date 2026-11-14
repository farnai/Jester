import React from "react";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "danger" | "brand" | "primaryDark";
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
      padding: "0.4rem 0.85rem",
      fontSize: "0.825rem",
      minHeight: "36px",
      gap: "0.4rem",
    },
    md: {
      padding: "0.6rem 1.25rem",
      fontSize: "0.9rem",
      minHeight: "44px", // Accessible 44px touch target
      gap: "0.5rem",
    },
    lg: {
      padding: "0.75rem 1.6rem",
      fontSize: "1rem",
      minHeight: "52px",
      gap: "0.6rem",
    },
  };

  const variantStyles: Record<string, React.CSSProperties> = {
    primary: {
      backgroundColor: "var(--jester-color-brand-primary)",
      color: "var(--jester-color-brand-text)", // ACCESSIBILITY FIX: 5.82:1 WCAG AA contrast (white on #FF7A2F is only 2.60:1)
      border: "1px solid var(--jester-color-brand-border)",
      fontWeight: 700,
    },
    brand: {
      backgroundColor: "var(--jester-color-brand-primary)",
      color: "var(--jester-color-brand-text)", // ACCESSIBILITY FIX: 5.82:1 WCAG AA contrast
      border: "1px solid var(--jester-color-brand-border)",
      boxShadow: "var(--jester-shadow-brand-glow)",
      fontWeight: 700,
    },
    primaryDark: {
      backgroundColor: "var(--jester-color-brand-dark)", // Dark-orange variant when white text is desired (6.47:1)
      color: "var(--jester-color-brand-dark-text)",
      border: "1px solid var(--jester-color-brand-dark-border)",
      fontWeight: 700,
    },
    secondary: {
      backgroundColor: "var(--jester-color-surface)",
      color: "var(--jester-color-text-primary)",
      border: "1px solid var(--jester-color-border-medium)",
      fontWeight: 600,
    },
    outline: {
      backgroundColor: "transparent",
      color: "var(--jester-color-text-primary)",
      border: "1px solid var(--jester-color-border-interactive)",
      fontWeight: 600,
    },
    ghost: {
      backgroundColor: "transparent",
      color: "var(--jester-color-text-secondary)",
      border: "1px solid transparent",
      fontWeight: 600,
    },
    danger: {
      backgroundColor: "var(--jester-color-danger-bg)",
      color: "var(--jester-color-danger-text)",
      border: "1px solid var(--jester-color-danger-border)",
      fontWeight: 600,
    },
  };

  const baseStyle: React.CSSProperties = {
    display: fullWidth ? "flex" : "inline-flex",
    width: fullWidth ? "100%" : "auto",
    alignItems: "center",
    justifyContent: "center",
    borderRadius: "12px",
    fontWeight: 700,
    cursor: isDisabled ? "not-allowed" : "pointer",
    opacity: isDisabled ? 0.55 : 1,
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
