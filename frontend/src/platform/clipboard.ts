export interface ClipboardFacade {
  setString: (text: string) => Promise<boolean>;
  getString: () => Promise<string>;
}

/**
 * Universal Clipboard Facade:
 * Web: Uses navigator.clipboard.
 * Native: Target for expo-clipboard.
 */
export const clipboard: ClipboardFacade = {
  setString: async (text: string): Promise<boolean> => {
    if (typeof window !== "undefined" && navigator.clipboard) {
      try {
        await navigator.clipboard.writeText(text);
        return true;
      } catch {}
    }
    return false;
  },
  getString: async (): Promise<string> => {
    if (typeof window !== "undefined" && navigator.clipboard) {
      try {
        return await navigator.clipboard.readText();
      } catch {}
    }
    return "";
  },
};
