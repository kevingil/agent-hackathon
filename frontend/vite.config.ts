import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // equivalent to 0.0.0.0
    port: 5173,
    proxy: {
      "/api": "http://backend:5000",
    },
  },
});
