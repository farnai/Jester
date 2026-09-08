export interface NotificationsFacade {
  requestPermissions: () => Promise<boolean>;
  getPushToken: () => Promise<string | null>;
  scheduleLocalNotification: (title: string, body: string) => Promise<void>;
}

/**
 * Universal Notifications Facade:
 * Web: Uses Notification API if supported; otherwise logs or degrades gracefully.
 * Native: Target for expo-notifications.
 */
export const notifications: NotificationsFacade = {
  requestPermissions: async (): Promise<boolean> => {
    if (typeof window !== "undefined" && "Notification" in window) {
      const permission = await Notification.requestPermission();
      return permission === "granted";
    }
    return false;
  },
  getPushToken: async (): Promise<string | null> => {
    // On web, web-push registration or Supabase web channel is used
    return null;
  },
  scheduleLocalNotification: async (title: string, body: string): Promise<void> => {
    if (typeof window !== "undefined" && "Notification" in window && Notification.permission === "granted") {
      try {
        new Notification(title, { body, icon: "/favicon.ico" });
      } catch {}
    }
  },
};
