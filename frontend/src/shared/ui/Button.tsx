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
      backgroundColor: "#FF7A2F",
      color: "#222630", // ACCESSIBILITY FIX: 5.82:1 WCAG AA contrast (white on #FF7A2F is only 2.60:1)
      border: "1px solid #E9681F",
      fontWeight: 700,
    },
    brand: {
      backgroundColor: "#FF7A2F",
      color: "#222630", // ACCESSIBILITY FIX: 5.82:1 WCAG AA contrast
      border: "1px solid #E9681F",
      boxShadow: "0 2px 6px rgba(255, 122, 47, 0.22)",
      fontWeight: 700,
    },
    primaryDark: {
      backgroundColor: "#9E4215", // Dark-orange variant when white text is desired (6.47:1)
      color: "#FFFFFF",
      border: "1px solid #713111",
      fontWeight: 700,
    },
    secondary: {
      backgroundColor: "#FFFFFF",
      color: "#222630",
      border: "1px solid #D8D1C7",
      fontWeight: 600,
    },
    outline: {
      backgroundColor: "transparent",
      color: "#222630",
      border: "1px solid #8F8A83",
      fontWeight: 600,
    },
    ghost: {
      backgroundColor: "transparent",
      color: "#6A716F",
      border: "1px solid transparent",
      fontWeight: 600,
    },
    danger: {
      backgroundColor: "#FBE9E8",
      color: "#AE3534",
      border: "1px solid #F5C6C5",
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
