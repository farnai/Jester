export interface ShareFacade {
  share: (content: { title?: string; message: string; url?: string }) => Promise<boolean>;
}

/**
 * Universal Share Facade:
 * Web: Uses navigator.share if available; otherwise falls back to clipboard copy.
 * Native: Target for Share.share from react-native or expo-sharing.
 */
export const share: ShareFacade = {
  share: async ({ title, message, url }): Promise<boolean> => {
    if (typeof window !== "undefined" && navigator.share) {
      try {
        await navigator.share({ title, text: message, url });
        return true;
      } catch (e: any) {
        if (e.name === "AbortError") return false;
      }
    }
    // Fallback: Copy to clipboard if navigator.clipboard is available
    if (typeof window !== "undefined" && navigator.clipboard) {
      try {
        const fullText = [title, message, url].filter(Boolean).join(" - ");
        await navigator.clipboard.writeText(fullText);
        return true;
      } catch {}
    }
    return false;
  },
};
