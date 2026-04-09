import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { viteSingleFile } from "vite-plugin-singlefile";
import { synapseVite } from "@nimblebrain/synapse/vite";

export default defineConfig({
  plugins: [
    react(),
    viteSingleFile(),
    synapseVite(),
    // Zero config — reads ../manifest.json automatically.
    // Starts the MCP server, serves preview at /__preview.
    //
    // Override if needed:
    //   synapseVite({ appName: "hello", serverCmd: "uv run python -m mcp_hello.server" })
  ],
  build: {
    outDir: "dist",
    assetsInlineLimit: Infinity,
  },
});
