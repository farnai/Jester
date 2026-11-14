import React from "react";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "brand" | "score" | "success" | "warning" | "danger" | "astrology" | "outline";
  size?: "sm" | "md";
  icon?: React.ReactNode;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = "default",
  size = "md",
  icon,
  style,
  className = "",
  ...rest
}) => {
  const variantStyles: Record<string, React.CSSProperties> = {
    default: {
      backgroundColor: "var(--jester-color-surface-subtle)",
      color: "var(--jester-color-text-secondary)",
      border: "1px solid var(--jester-color-border-subtle)",
    },
    brand: {
      backgroundColor: "var(--jester-color-brand-subtle)",
      color: "var(--jester-color-brand-subtle-text)",
      border: "1px solid var(--jester-color-brand-subtle-border)",
    },
    score: {
      backgroundColor: "var(--jester-color-insight-peach-bg)",
      color: "var(--jester-color-insight-peach-text)",
      border: "1px solid var(--jester-color-insight-peach-border)",
      fontWeight: 700,
    },
    success: {
      backgroundColor: "var(--jester-color-success-bg)",
      color: "var(--jester-color-success-text)",
      border: "1px solid var(--jester-color-success-border)",
    },
    warning: {
      backgroundColor: "var(--jester-color-warning-bg)",
      color: "var(--jester-color-warning-text)",
      border: "1px solid var(--jester-color-warning-border)",
    },
    danger: {
      backgroundColor: "var(--jester-color-danger-bg)",
      color: "var(--jester-color-danger-text)",
      border: "1px solid var(--jester-color-danger-border)",
    },
    astrology: {
      backgroundColor: "var(--jester-color-astrology-bg)",
      color: "var(--jester-color-astrology-text)",
      border: "1px solid var(--jester-color-astrology-border)",
    },
    outline: {
      backgroundColor: "transparent",
      color: "var(--jester-color-text-secondary)",
      border: "1px solid var(--jester-color-border-medium)",
    },
  };

  const sizeStyles: Record<string, React.CSSProperties> = {
    sm: {
      padding: "0.15rem 0.45rem",
      fontSize: "0.725rem",
      borderRadius: "6px",
      gap: "0.25rem",
    },
    md: {
      padding: "0.25rem 0.65rem",
      fontSize: "0.8rem",
      borderRadius: "8px",
      gap: "0.35rem",
    },
  };

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        fontWeight: 600,
        lineHeight: 1.2,
        boxSizing: "border-box",
        ...sizeStyles[size],
        ...variantStyles[variant],
        ...style,
      }}
      className={`jester-badge ${className}`}
      {...rest}
    >
      {icon && <span style={{ display: "flex", alignItems: "center" }}>{icon}</span>}
      <span>{children}</span>
    </span>
  );
};
