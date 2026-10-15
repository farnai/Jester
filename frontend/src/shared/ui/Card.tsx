import React from "react";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  interactive?: boolean;
  padded?: boolean;
  variant?: "default" | "elevated" | "accent" | "bordered" | "calm" | "subtle";
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
      backgroundColor: "#FFFFFF",
      border: "1px solid #E6E0D7",
      boxShadow: "0 1px 3px rgba(34, 38, 48, 0.04)",
    },
    elevated: {
      backgroundColor: "#FFFFFF",
      border: "1px solid #E6E0D7",
      boxShadow: "0 4px 14px rgba(34, 38, 48, 0.06)",
    },
    accent: {
      // Warm peach insight card
      backgroundColor: "#FBEEE7",
      border: "1px solid #F5DDD1",
      boxShadow: "0 1px 4px rgba(255, 122, 47, 0.06)",
    },
    calm: {
      // Measured sage supportive insight card
      backgroundColor: "#E8EFE2",
      border: "1px solid #D6E1CD",
    },
    subtle: {
      // Warm alt surface card
      backgroundColor: "#F3EEE6",
      border: "1px solid #E6E0D7",
    },
    bordered: {
      backgroundColor: "#FFFFFF",
      border: "1.5px solid #D8D1C7",
    },
  };

  const cardStyle: React.CSSProperties = {
    borderRadius: "16px",
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
