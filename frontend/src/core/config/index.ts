const isBrowser = typeof window !== "undefined";
const currentOrigin = isBrowser ? window.location.origin : "http://127.0.0.1:3000";

// When accessed via an external tunnel or LAN IP, route requests through Vite proxy
const isExternalAccess =
  isBrowser &&
  !window.location.hostname.includes("127.0.0.1") &&
  !window.location.hostname.includes("localhost");

export const CONFIG = {
  SUPABASE_URL:
    isExternalAccess
      ? currentOrigin
      : (import.meta.env.VITE_SUPABASE_URL || "http://127.0.0.1:54321"),
  SUPABASE_ANON_KEY:
    import.meta.env.VITE_SUPABASE_ANON_KEY ||
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0",
  API_BASE_URL:
    isExternalAccess
      ? ""
      : (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"),
};
