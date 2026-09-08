export interface StorageFacade {
  getItem: (key: string) => Promise<string | null>;
  setItem: (key: string, value: string) => Promise<void>;
  removeItem: (key: string) => Promise<void>;
}

/**
 * Universal Storage Facade:
 * Web: Uses localStorage with fail-safe error handling.
 * Native: Target for expo-secure-store hardware encryption.
 */
export const storage: StorageFacade = {
  getItem: async (key: string): Promise<string | null> => {
    try {
      if (typeof window !== "undefined" && window.localStorage) {
        return window.localStorage.getItem(key);
      }
    } catch {
      // Storage access blocked or unavailable
    }
    return null;
  },
  setItem: async (key: string, value: string): Promise<void> => {
    try {
      if (typeof window !== "undefined" && window.localStorage) {
        window.localStorage.setItem(key, value);
      }
    } catch {
      // Storage access blocked or unavailable
    }
  },
  removeItem: async (key: string): Promise<void> => {
    try {
      if (typeof window !== "undefined" && window.localStorage) {
        window.localStorage.removeItem(key);
      }
    } catch {
      // Storage access blocked or unavailable
    }
  },
};
