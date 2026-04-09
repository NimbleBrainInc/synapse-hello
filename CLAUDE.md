# Hello World MCP App

Reference implementation for MCP apps with UIs. Two-project architecture: Python MCP server + React/Vite UI with Synapse SDK.

## Architecture

```
hello/
├── src/mcp_hello/          Python MCP server (FastMCP)
│   ├── server.py           Tools + ui:// resource
│   └── ui.py               Loads ui/dist/index.html, falls back to inline HTML
└── ui/                     React + Vite project
    ├── src/App.tsx          React components using Synapse hooks
    ├── vite.config.ts       synapseVite() plugin — auto-starts server in dev
    └── dist/index.html      Built single-file bundle (vite-plugin-singlefile)
```

**How it connects:** The Python server serves `ui/dist/index.html` as a `ui://hello/main` MCP resource. Hosts that support ext-apps render it in an iframe. The Synapse SDK inside the iframe communicates with the host via postMessage JSON-RPC.

## Commands

```bash
# Development (starts MCP server + Vite HMR + preview host)
cd ui && npm run dev
# Open http://localhost:5173/__preview

# Build UI for production
cd ui && npm run build

# Run server standalone (stdio — for Claude Desktop, MCP clients)
uv run python -m mcp_hello.server

# Run server HTTP (for direct API testing)
uv run uvicorn mcp_hello.server:app --port 8001

# Lint + typecheck
uv run ruff check src/
uv run ty check src/
```

## How the Vite plugin works

`synapseVite()` in `ui/vite.config.ts` does everything automatically:

1. Reads `../manifest.json` → gets app name (`@nimblebraininc/hello`) and server command (`python -m mcp_hello.server`)
2. Detects `pyproject.toml` → prepends `uv run` to the command
3. Spawns the MCP server as a child process in **stdio mode** (stdin/stdout JSON-RPC)
4. Serves a preview host page at `/__preview` that:
   - Iframes the Vite app at `/`
   - Completes the ext-apps handshake (Synapse initializes)
   - Proxies `tools/call` from the iframe through `POST /__mcp` to the stdio server
   - Provides dark/light theme toggle
5. HMR works inside the iframe — `.tsx` edits appear instantly

## How the UI talks to the server

```
Browser (localhost:5173/__preview)
├── Host page (bridge)
│   ├── Handles ext-apps handshake → Synapse.ready resolves
│   ├── Receives tools/call postMessage → POST /__mcp → stdin to MCP server
│   └── Receives JSON-RPC response from stdout → postMessage back to iframe
└── Iframe (localhost:5173/)
    └── React app with SynapseProvider
        ├── useCallTool("get_greeting") → synapse.callTool() → postMessage to host
        ├── useDataSync() → listens for synapse/data-changed from host
        └── useTheme() → reads tokens from handshake, updates on synapse/theme-changed
```

## Synapse hooks used in App.tsx

| Hook | Purpose |
|------|---------|
| `SynapseProvider` | Wraps app, creates Synapse instance, handles handshake |
| `useCallTool(name)` | Returns `{ call, isPending, data, error }` — call tools with loading state |
| `useDataSync(cb)` | Fires callback when agent calls a tool on this server |
| `useTheme()` | Returns `{ mode, primaryColor, tokens }` — reactive, re-renders on change |

## Server tools

| Tool | Input | Output |
|------|-------|--------|
| `get_greeting` | `{ name: string }` | `"Hello, {name}! 👋"` |
| `get_greet_count` | `{}` | `"{count}"` (string) |

## UI resource

`ui://hello/main` — served by `hello_ui()` in `server.py`. Calls `load_ui()` which:
1. Checks `ui/dist/index.html` — if exists, returns the built React bundle
2. Falls back to `FALLBACK_HTML` — minimal inline HTML that works without Synapse or a build step

## Build pipeline

`ui/vite.config.ts` uses `vite-plugin-singlefile` which inlines all JS/CSS into a single `index.html`. No external assets. This file is what the MCP server reads and serves.

**Production build:** `cd ui && npm run build` → `ui/dist/index.html` (single file, ~200KB, ~64KB gzipped)

**MCPB bundle:** `.github/workflows/release.yml` runs `cd ui && npm ci && npm run build` before `mcpb-pack`. The `.mcpbignore` excludes `ui/node_modules/` and `ui/src/` but includes `ui/dist/`.

## Cross-host behavior

- **NimbleBrain:** Full Synapse features (data sync, visible state, keyboard forwarding, theme)
- **Synapse Preview (/__preview):** Tool calls + theme toggle. No data sync from agent.
- **Claude Desktop:** Tools work via stdio. No UI rendering (ext-apps not supported yet).
- **Any MCP client:** Tools work. UI depends on host ext-apps support.

Synapse detects the host during handshake (`serverInfo.name`). In non-NimbleBrain hosts, NB-specific hooks (`useDataSync`, `setVisibleState`, `action`, `chat`) become silent no-ops. `useCallTool` and `useTheme` work in any ext-apps host.

## Conventions

- **Python:** ruff for linting/formatting, ty for type checking, uv for package management
- **UI:** TypeScript strict mode, React 19, Vite 6
- **Versioning:** `make bump VERSION=x.y.z` updates manifest.json + pyproject.toml + __init__.py
