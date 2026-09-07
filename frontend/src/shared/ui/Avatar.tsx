import React from "react";

export interface AvatarProps {
  src?: string | null;
  name?: string | null;
  size?: "xs" | "sm" | "md" | "lg" | "xl";
  alt?: string;
  style?: React.CSSProperties;
}

export const Avatar: React.FC<AvatarProps> = ({
  src,
  name = "User",
  size = "md",
  alt,
  style,
}) => {
  const sizeMap: Record<string, { size: number; font: string }> = {
    xs: { size: 24, font: "0.7rem" },
    sm: { size: 32, font: "0.8rem" },
    md: { size: 44, font: "1rem" },
    lg: { size: 56, font: "1.25rem" },
    xl: { size: 72, font: "1.6rem" },
  };

  const { size: dimension, font } = sizeMap[size];

  const getInitials = (n?: string | null) => {
    if (!n) return "👤";
    const parts = n.trim().split(" ");
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return n.slice(0, 2).toUpperCase();
  };

  // Deterministic color palette for avatar fallback
  const getBgColor = (n?: string | null) => {
    if (!n) return "#6366f1";
    const colors = [
      "#6366f1", // indigo
      "#8b5cf6", // purple
      "#ec4899", // pink
      "#06b6d4", // cyan
      "#10b981", // emerald
      "#f59e0b", // amber
      "#3b82f6", // blue
    ];
    let hash = 0;
    for (let i = 0; i < n.length; i++) {
      hash = n.charCodeAt(i) + ((hash << 5) - hash);
    }
    return colors[Math.abs(hash) % colors.length];
  };

  if (src) {
    return (
      <img
        src={src}
        alt={alt || name || "User Avatar"}
        style={{
          width: `${dimension}px`,
          height: `${dimension}px`,
          borderRadius: "50%",
          objectFit: "cover",
          border: "2px solid #ffffff",
          boxShadow: "0 1px 3px rgba(0, 0, 0, 0.1)",
          boxSizing: "border-box",
          ...style,
        }}
      />
    );
  }

  return (
    <div
      style={{
        width: `${dimension}px`,
        height: `${dimension}px`,
        borderRadius: "50%",
        backgroundColor: getBgColor(name),
        color: "#ffffff",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: font,
        fontWeight: 700,
        letterSpacing: "0.02em",
        border: "2px solid #ffffff",
        boxShadow: "0 1px 3px rgba(0, 0, 0, 0.1)",
        userSelect: "none",
        flexShrink: 0,
        boxSizing: "border-box",
        ...style,
      }}
      title={name || "User"}
    >
      {getInitials(name)}
    </div>
  );
};
