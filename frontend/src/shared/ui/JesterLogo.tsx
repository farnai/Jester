import React from "react";

export interface JesterHatIconProps extends React.SVGProps<SVGSVGElement> {
  size?: number;
}

export const JesterHatIcon: React.FC<JesterHatIconProps> = ({
  size = 36,
  className = "",
  style,
  ...props
}) => {
  return (
    <svg
      width={size}
      height={Math.round((size * 340) / 540)}
      viewBox="25 0 555 350"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      style={{ display: "inline-block", verticalAlign: "middle", ...style }}
      aria-label="JESTER hat symbol"
      {...props}
    >
      {/* Right panel - Espresso */}
      <path
        fill="#3A2A22"
        d="M370 164 C412 140 464 128 499 139 C532 149 552 166 561 197 C566 211 564 230 559 245 C529 199 487 194 450 214 C410 237 380 283 361 330 C375 262 382 217 370 164 Z"
      />
      {/* Center panel - Terracotta */}
      <path
        fill="#C7614B"
        d="M225 145 C244 102 277 55 309 25 C330 5 346 -1 358 6 C374 7 384 17 385 27 C365 15 345 29 338 54 C320 108 361 149 373 199 C387 254 374 308 361 330 C354 268 324 217 278 180 C257 162 242 152 225 145 Z"
      />
      {/* Left panel - Dusty Rose */}
      <path
        fill="#D9A69A"
        d="M51 246 C60 198 95 149 133 135 C163 122 189 128 225 145 C266 166 294 207 318 264 C278 241 247 275 235 330 C209 258 175 215 131 208 C90 201 66 223 51 246 Z"
      />
      {/* Central Overlap */}
      <path
        fill="#BC7464"
        d="M225 145 C262 165 291 211 318 264 C280 246 246 278 235 330 C213 272 207 222 212 184 C215 168 219 155 225 145 Z"
      />
      {/* Separator lines */}
      <path
        fill="#F8EFE6"
        d="M225 145 C286 172 335 233 351 279 C360 307 362 326 361 330 C354 276 329 225 279 185 C255 166 236 154 225 145 Z"
      />
      <path
        fill="#F8EFE6"
        d="M369 164 C380 204 381 257 361 330 C370 263 371 217 362 174 Z"
      />
      {/* Left Bell */}
      <g transform="translate(53, 259)">
        <circle r="22" fill="#C8966B" />
        <circle cx="-7" cy="-8" r="8" fill="#E9C3A2" />
        <path d="M-1 0 C-2 6 2 11 4 15" stroke="#3A2A22" strokeWidth="3.5" strokeLinecap="round" fill="none" />
        <circle cx="-2" cy="-1" r="3.5" fill="#3A2A22" />
      </g>
      {/* Center Bell */}
      <g transform="translate(381, 54)">
        <circle r="22" fill="#C8966B" />
        <circle cx="-7" cy="-8" r="8" fill="#E9C3A2" />
        <path d="M-1 0 C-2 6 2 11 4 15" stroke="#3A2A22" strokeWidth="3.5" strokeLinecap="round" fill="none" />
        <circle cx="-2" cy="-1" r="3.5" fill="#3A2A22" />
      </g>
      {/* Right Bell */}
      <g transform="translate(558, 259)">
        <circle r="22" fill="#C8966B" />
        <circle cx="-7" cy="-8" r="8" fill="#E9C3A2" />
        <path d="M-1 0 C-2 6 2 11 4 15" stroke="#3A2A22" strokeWidth="3.5" strokeLinecap="round" fill="none" />
        <circle cx="-2" cy="-1" r="3.5" fill="#3A2A22" />
      </g>
    </svg>
  );
};

export interface JesterLogoHorizontalProps {
  size?: "sm" | "md" | "lg";
  withSubtitle?: boolean;
  className?: string;
}

export const JesterLogoHorizontal: React.FC<JesterLogoHorizontalProps> = ({
  size = "md",
  withSubtitle = false,
  className = "",
}) => {
  const iconSize = size === "sm" ? 28 : size === "lg" ? 44 : 36;
  const wordmarkSize = size === "sm" ? "1.25rem" : size === "lg" ? "1.85rem" : "1.5rem";

  return (
    <div
      className={`inline-flex items-center gap-2.5 select-none ${className}`}
      style={{ display: "inline-flex", alignItems: "center" }}
    >
      <JesterHatIcon size={iconSize} />
      <div style={{ display: "flex", flexDirection: "column", lineHeight: 1 }}>
        <span
          style={{
            fontFamily: "'GFS Didot', 'Didot', 'Bodoni MT', 'Cinzel', 'Georgia', serif",
            fontWeight: 700,
            fontSize: wordmarkSize,
            letterSpacing: "0.18em",
            color: "#3A2A22",
            textTransform: "uppercase",
          }}
        >
          JESTER
        </span>
        {withSubtitle && (
          <span
            style={{
              fontSize: "0.62rem",
              letterSpacing: "0.12em",
              color: "#6A716F",
              marginTop: "2px",
              fontFamily: "system-ui, sans-serif",
            }}
          >
            People Discovery • Relationship Intelligence
          </span>
        )}
      </div>
    </div>
  );
};
