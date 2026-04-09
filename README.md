# Hello World MCP App

Minimal reference implementation for building MCP apps with UIs. Python server (FastMCP) + React UI (Synapse SDK).

## Quick Start

```bash
# Install server deps
uv sync

# Install UI deps + build
cd ui && npm install && npm run build && cd ..

# Preview (standalone — no NimbleBrain needed)
npx @nimblebrain/synapse preview \
  --server "uv run uvicorn mcp_hello.server:app --port 8001" \
  --ui ./ui

# Open http://localhost:5180
```

## Development

### UI hot-reload (standalone)

```bash
npx @nimblebrain/synapse preview \
  --server "uv run uvicorn mcp_hello.server:app --port 8001" \
  --ui ./ui
```

This starts three things:
- **:8001** — MCP server (uvicorn, your Python tools)
- **:5173** — Vite dev server (React UI with HMR)
- **:5180** — Preview harness (minimal bridge host)

Edit `ui/src/App.tsx` — changes appear instantly at `localhost:5180`.

### UI hot-reload (NimbleBrain)

```bash
cd products/nimblebrain/code
bun run dev --app /path/to/mcp-servers/hello/ui
```

Full platform with Synapse runtime injection, data sync, and all host features.

### Tools only (no UI)

```bash
# stdio mode (Claude Desktop, any MCP client)
uv run python -m mcp_hello.server

# HTTP mode (direct API testing)
uv run uvicorn mcp_hello.server:app --port 8001
```

## Project Structure

```
hello/
├── manifest.json              MCPB bundle manifest
├── pyproject.toml             Python project config
├── src/mcp_hello/
│   ├── server.py              MCP server: tools + UI resource
│   └── ui.py                  Loads built HTML or inline fallback
└── ui/                        Vite + React project
    ├── package.json
    ├── vite.config.ts
    ├── index.html             Entry point
    └── src/
        ├── main.tsx           React mount
        └── App.tsx            Components with Synapse hooks
```

## How It Works

1. `server.py` defines MCP tools (`get_greeting`, `get_greet_count`) and a UI resource (`ui://hello/main`)
2. `ui.py` loads `ui/dist/index.html` (the built single-file React bundle) and serves it as the resource
3. The UI uses Synapse hooks (`useCallTool`, `useDataSync`, `useTheme`) for tool calls and host integration
4. Vite + `vite-plugin-singlefile` bundles everything into one HTML file — no external assets

## Cross-Host Compatibility

| Host | Tools | UI | Synapse Features |
|------|-------|----|------------------|
| NimbleBrain | Full | Full (React + Synapse) | Data sync, theme, keyboard forwarding |
| Synapse Preview | Full | Full (React + Synapse) | Tool calls, theme toggle |
| Claude Desktop | Full | Not yet | N/A |
| Any MCP client | Full | Depends on host | Graceful degradation |
