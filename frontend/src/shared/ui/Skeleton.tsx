import React from "react";

export interface SkeletonProps {
  width?: string | number;
  height?: string | number;
  borderRadius?: string | number;
  circle?: boolean;
  style?: React.CSSProperties;
  className?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  width = "100%",
  height = "1.2rem",
  borderRadius = "6px",
  circle = false,
  style,
  className = "",
}) => {
  return (
    <div
      className={`jester-skeleton ${className}`}
      style={{
        width: circle ? height : width,
        height,
        borderRadius: circle ? "50%" : borderRadius,
        backgroundColor: "var(--jester-primitive-slate-200, #e2e8f0)",
        backgroundImage: "linear-gradient(90deg, var(--jester-primitive-slate-200, #e2e8f0) 0px, var(--jester-primitive-slate-100, #f1f5f9) 40px, var(--jester-primitive-slate-200, #e2e8f0) 80px)",
        backgroundSize: "600px",
        animation: "shimmer 1.6s infinite linear",
        ...style,
      }}
    />
  );
};
