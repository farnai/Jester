export interface HapticsFacade {
  light: () => void;
  medium: () => void;
  heavy: () => void;
  success: () => void;
  error: () => void;
}

/**
 * Universal Haptics Facade:
 * Web: Uses navigator.vibrate if available; otherwise performs a graceful no-op.
 * Native: Target for expo-haptics impactAsync / notificationAsync.
 */
export const haptics: HapticsFacade = {
  light: () => {
    if (typeof window !== "undefined" && "vibrate" in navigator) {
      try {
        navigator.vibrate(10);
      } catch {}
    }
  },
  medium: () => {
    if (typeof window !== "undefined" && "vibrate" in navigator) {
      try {
        navigator.vibrate(20);
      } catch {}
    }
  },
  heavy: () => {
    if (typeof window !== "undefined" && "vibrate" in navigator) {
      try {
        navigator.vibrate(35);
      } catch {}
    }
  },
  success: () => {
    if (typeof window !== "undefined" && "vibrate" in navigator) {
      try {
        navigator.vibrate([15, 50, 20]);
      } catch {}
    }
  },
  error: () => {
    if (typeof window !== "undefined" && "vibrate" in navigator) {
      try {
        navigator.vibrate([30, 40, 30]);
      } catch {}
    }
  },
};
