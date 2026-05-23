import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-member-access
  const p: string = path.join(process.cwd(), "..");
  const env = loadEnv(mode, p, "FRONTEND");
  return {
    plugins: [react()],
    server: {
      port: env.FRONTEND_PORT ? +env.FRONTEND_PORT : 5173,
    },
    envPrefix: "FRONTEND",
    envDir: "..",
  };
});
