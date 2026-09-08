export const motion = {
  duration: {
    fast: 150,
    normal: 250,
    slow: 350,
  },
  easing: {
    easeInOut: "ease-in-out",
    easeOut: "ease-out",
    easeIn: "ease-in",
    linear: "linear",
  },
} as const;

export type MotionTokens = typeof motion;
