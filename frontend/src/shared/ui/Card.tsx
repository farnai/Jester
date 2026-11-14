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
      backgroundColor: "var(--jester-color-surface)",
      border: "1px solid var(--jester-color-border-subtle)",
      boxShadow: "var(--jester-shadow-card-subtle)",
    },
    elevated: {
      backgroundColor: "var(--jester-color-surface)",
      border: "1px solid var(--jester-color-border-subtle)",
      boxShadow: "var(--jester-shadow-card-elevated)",
    },
    accent: {
      // Warm peach insight card
      backgroundColor: "var(--jester-color-insight-peach-bg)",
      border: "1px solid var(--jester-color-insight-peach-border)",
      boxShadow: "var(--jester-shadow-brand-sm, 0 1px 4px color-mix(in srgb, var(--jester-primitive-orange-500) 6%, transparent))",
    },
    calm: {
      // Measured sage supportive insight card
      backgroundColor: "var(--jester-color-insight-sage-bg)",
      border: "1px solid var(--jester-color-insight-sage-border)",
    },
    subtle: {
      // Warm alt surface card
      backgroundColor: "var(--jester-color-surface-subtle)",
      border: "1px solid var(--jester-color-border-subtle)",
    },
    bordered: {
      backgroundColor: "var(--jester-color-surface)",
      border: "1.5px solid var(--jester-color-border-medium)",
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
