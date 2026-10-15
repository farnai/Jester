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
      backgroundColor: "#F3EEE6",
      color: "#6A716F",
      border: "1px solid #E6E0D7",
    },
    brand: {
      backgroundColor: "#FFE7D7",
      color: "#713111",
      border: "1px solid #FFD0B2",
    },
    score: {
      backgroundColor: "#FBEEE7",
      color: "#9E4215",
      border: "1px solid #F5DDD1",
      fontWeight: 700,
    },
    success: {
      backgroundColor: "#EAF4EA",
      color: "#4B6242",
      border: "1px solid #BACAAC",
    },
    warning: {
      backgroundColor: "#FFF3DE",
      color: "#925C18",
      border: "1px solid #FFE0B2",
    },
    danger: {
      backgroundColor: "#FBE9E8",
      color: "#AE3534",
      border: "1px solid #F5C6C5",
    },
    astrology: {
      backgroundColor: "#E8EFE2",
      color: "#4B6242",
      border: "1px solid #D6E1CD",
    },
    outline: {
      backgroundColor: "transparent",
      color: "#6A716F",
      border: "1px solid #D8D1C7",
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
