export interface LinkingFacade {
  openURL: (url: string) => Promise<boolean>;
  canOpenURL: (url: string) => Promise<boolean>;
}

/**
 * Universal Linking Facade:
 * Web: Uses window.open.
 * Native: Target for expo-linking or Linking.openURL.
 */
export const linking: LinkingFacade = {
  openURL: async (url: string): Promise<boolean> => {
    if (typeof window !== "undefined") {
      window.open(url, "_blank");
      return true;
    }
    return false;
  },
  canOpenURL: async (_url: string): Promise<boolean> => {
    return true;
  },
};
