import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig, loadEnv } from "vite"

export default defineConfig(({ mode }) => {
  // Load ALL env vars from root directory (empty prefix = load all)
  const env = loadEnv(mode, path.resolve(__dirname, ".."), "")

  return {
    plugins: [react()],
    envDir: "..",
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    server: {
      port: 3000,
      host: true,
      proxy: {
        "/athena": {
          target: "http://localhost:3001",
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/athena/, "/api"),
        },
      },
    },
    define: {
      // Map shared vars to VITE_ namespace for frontend access
      "import.meta.env.VITE_SUPABASE_URL": JSON.stringify(env.SUPABASE_URL),
      "import.meta.env.VITE_SUPABASE_ANON_KEY": JSON.stringify(env.SUPABASE_ANON_KEY),
    },
  }
})
