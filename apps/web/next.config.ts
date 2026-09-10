import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["@afrosite/contracts", "@afrosite/llm"],
};

export default nextConfig;
