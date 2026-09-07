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
      backgroundColor: "#f1f5f9",
      color: "#475569",
      border: "1px solid #e2e8f0",
    },
    brand: {
      backgroundColor: "#eef2ff",
      color: "#4338ca",
      border: "1px solid #c7d2fe",
    },
    score: {
      backgroundColor: "#fdf4ff",
      color: "#9333ea",
      border: "1px solid #f0abfc",
      fontWeight: 700,
    },
    success: {
      backgroundColor: "#f0fdf4",
      color: "#15803d",
      border: "1px solid #bbf7d0",
    },
    warning: {
      backgroundColor: "#fffbeb",
      color: "#b45309",
      border: "1px solid #fde68a",
    },
    danger: {
      backgroundColor: "#fef2f2",
      color: "#b91c1c",
      border: "1px solid #fecaca",
    },
    astrology: {
      backgroundColor: "#faf5ff",
      color: "#7e22ce",
      border: "1px solid #e9d5ff",
    },
    outline: {
      backgroundColor: "transparent",
      color: "#64748b",
      border: "1px solid #cbd5e1",
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
