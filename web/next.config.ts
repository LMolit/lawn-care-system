import type { NextConfig } from "next";
import path from "node:path";

const nextConfig: NextConfig = {
  output: "standalone",
  // The repo root, so Next copies in dependencies hoisted by pnpm workspaces
  outputFileTracingRoot: path.join(__dirname, ".."),
};

export default nextConfig;
