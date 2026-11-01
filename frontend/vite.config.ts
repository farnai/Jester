import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    allowedHosts: true,
    proxy: {
      "/v1": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
      "/auth/v1": {
        target: "http://127.0.0.1:54321",
        changeOrigin: true,
      },
      "/rest/v1": {
        target: "http://127.0.0.1:54321",
        changeOrigin: true,
      },
      "/storage/v1": {
        target: "http://127.0.0.1:54321",
        changeOrigin: true,
      },
      "/realtime/v1": {
        target: "http://127.0.0.1:54321",
        changeOrigin: true,
        ws: true,
      },
    },
  },
  resolve: {
    alias: {
      "react-native": "react-native-web",
    },
    extensions: [
      ".web.tsx",
      ".web.ts",
      ".web.jsx",
      ".web.js",
      ".tsx",
      ".ts",
      ".jsx",
      ".js",
    ],
  },
  define: {
    global: "window",
  },
});
