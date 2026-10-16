import React from "react";
import logoSvg from "../../assets/brand/JESTER_Logo_Stacked_Outlined.svg";

interface JesterLogoProps {
  variant?: "stacked" | "horizontal" | "icon" | "wordmark";
  height?: number;
  className?: string;
  style?: React.CSSProperties;
}

export const JesterLogo: React.FC<JesterLogoProps> = ({
  variant = "horizontal",
  height = 32,
  className = "",
  style = {},
}) => {
  if (variant === "icon") {
    const width = Math.round(height * (560 / 340));
    return (
      <svg
        viewBox="320 50 560 340"
        aria-label="JESTER Icon"
        width={width}
        height={height}
        className={className}
        style={{ display: "inline-block", verticalAlign: "middle", ...style }}
      >
        <image href={logoSvg} width="1200" height="700" />
      </svg>
    );
  }

  if (variant === "wordmark") {
    const width = Math.round(height * (720 / 150));
    return (
      <svg
        viewBox="240 430 720 150"
        aria-label="JESTER"
        width={width}
        height={height}
        className={className}
        style={{ display: "inline-block", verticalAlign: "middle", ...style }}
      >
        <image href={logoSvg} width="1200" height="700" />
      </svg>
    );
  }

  if (variant === "stacked") {
    const width = Math.round(height * (720 / 530));
    return (
      <svg
        viewBox="240 50 720 530"
        aria-label="JESTER"
        width={width}
        height={height}
        className={className}
        style={{ display: "inline-block", verticalAlign: "middle", ...style }}
      >
        <image href={logoSvg} width="1200" height="700" />
      </svg>
    );
  }

  // "horizontal" default: hat on the left, name on the right
  const hatWidth = Math.round(height * 1.5);
  const nameWidth = Math.round(height * 3.6);

  return (
    <span
      className={`jester-brand-logo ${className}`}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: `${Math.max(6, Math.round(height * 0.28))}px`,
        lineHeight: 1,
        ...style,
      }}
    >
      <svg
        viewBox="320 50 560 340"
        aria-hidden="true"
        width={hatWidth}
        height={height}
        style={{ display: "block" }}
      >
        <image href={logoSvg} width="1200" height="700" />
      </svg>
      <svg
        viewBox="240 430 720 150"
        aria-hidden="true"
        width={nameWidth}
        height={Math.round(height * 0.9)}
        style={{ display: "block" }}
      >
        <image href={logoSvg} width="1200" height="700" />
      </svg>
    </span>
  );
};

export default JesterLogo;
