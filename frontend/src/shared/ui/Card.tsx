import React from "react";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  interactive?: boolean;
  padded?: boolean;
  variant?: "default" | "elevated" | "accent" | "bordered";
}

export const Card: React.FC<CardProps> = ({
  children,
  interactive = false,
  padded = true,
  variant = "default",
  style,
  className = "",
  ...rest
}) => {
  const variantStyles: Record<string, React.CSSProperties> = {
    default: {
      backgroundColor: "#ffffff",
      border: "1px solid #e2e8f0",
      boxShadow: "0 1px 3px rgba(0, 0, 0, 0.04)",
    },
    elevated: {
      backgroundColor: "#ffffff",
      border: "1px solid #e2e8f0",
      boxShadow: "0 4px 12px rgba(0, 0, 0, 0.05)",
    },
    accent: {
      backgroundColor: "#fdf4ff",
      border: "1px solid #f0abfc",
      boxShadow: "0 1px 4px rgba(192, 38, 211, 0.06)",
    },
    bordered: {
      backgroundColor: "#ffffff",
      border: "2px solid #cbd5e1",
    },
  };

  const cardStyle: React.CSSProperties = {
    borderRadius: "12px",
    padding: padded ? "1.25rem" : 0,
    cursor: interactive ? "pointer" : "default",
    transition: "all 0.2s ease-in-out",
    boxSizing: "border-box",
    ...variantStyles[variant],
    ...style,
  };

  return (
    <div
      style={cardStyle}
      className={`jester-card ${interactive ? "interactive" : ""} ${className}`}
      {...rest}
    >
      {children}
    </div>
  );
};
