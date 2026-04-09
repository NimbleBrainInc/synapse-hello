"""UI resource loader for Hello World MCP App.

In development: run `cd ui && npm run dev` for HMR via Vite.
In production: `cd ui && npm run build` produces a single-file HTML bundle
at ui/dist/index.html, which the server reads and serves as a ui:// resource.

Fallback: if no built UI exists (e.g., running from a raw mpak install),
serves a minimal inline HTML that works without Synapse.
"""

from pathlib import Path

_UI_DIR = Path(__file__).resolve().parent.parent.parent / "ui" / "dist"


def load_ui() -> str:
    """Load the built single-file HTML, or fall back to inline HTML."""
    built = _UI_DIR / "index.html"
    if built.exists():
        return built.read_text()
    return FALLBACK_HTML


# Minimal fallback — works without Synapse, without a build step.
# Used when the UI hasn't been built yet or in stripped-down distributions.
FALLBACK_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: var(--font-sans, -apple-system, BlinkMacSystemFont, sans-serif);
    background: var(--color-background-primary, #fff);
    color: var(--color-text-primary, #1a1a1a);
    display: flex; align-items: center; justify-content: center;
    min-height: 100vh; padding: 2rem;
  }
  .container { max-width: 420px; width: 100%; }
  h1 { font-size: 1.5rem; margin-bottom: 1.5rem; }
  .row { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
  input {
    flex: 1; padding: 0.6rem 0.75rem; border-radius: 6px;
    border: 1px solid var(--color-border-primary, #e5e7eb);
    background: var(--color-background-secondary, #f9fafb); font-size: 0.95rem;
  }
  button {
    padding: 0.6rem 1.25rem; border-radius: 6px; border: none;
    background: var(--color-text-accent, #2563eb); color: #fff;
    font-size: 0.95rem; cursor: pointer; font-weight: 500;
  }
  button:disabled { opacity: 0.5; }
  .result {
    margin-top: 1rem; padding: 1rem; border-radius: 8px;
    background: var(--color-background-secondary, #f9fafb);
    border: 1px solid var(--color-border-primary, #e5e7eb);
    font-size: 1.1rem; min-height: 3rem;
  }
  .count { margin-top: 0.75rem; color: var(--color-text-secondary, #6b7280); font-size: 0.85rem; }
</style>
</head>
<body>
<div class="container">
  <h1>Hello 👋</h1>
  <div class="row">
    <input type="text" id="name" placeholder="Enter a name…" autofocus />
    <button id="btn">Greet</button>
  </div>
  <div class="result" id="result">Type a name and click Greet.</div>
  <div class="count" id="count"></div>
</div>
<script>
(function () {
  var pending = {};
  function callTool(name, args) {
    return new Promise(function (res, rej) {
      var id = crypto.randomUUID();
      pending[id] = { resolve: res, reject: rej };
      window.parent.postMessage({ jsonrpc: "2.0", id: id, method: "tools/call",
        params: { name: name, arguments: args || {} } }, "*");
      setTimeout(function () { if (pending[id]) { delete pending[id]; rej(new Error("Timeout")); } }, 10000);
    });
  }
  function text(r) {
    if (!r) return "";
    if (Array.isArray(r.content)) return r.content.map(function(c){return c.text||"";}).join("");
    return typeof r === "string" ? r : JSON.stringify(r);
  }
  window.addEventListener("message", function (e) {
    var m = e.data;
    if (!m || m.jsonrpc !== "2.0") return;
    if (m.id && pending[m.id]) {
      var p = pending[m.id]; delete pending[m.id];
      m.error ? p.reject(new Error(m.error.message)) : p.resolve(m.result);
    }
    if (m.method === "synapse/data-changed") refresh();
    if (m.method === "ui/initialize" && m.params?.theme?.tokens) {
      var t = m.params.theme.tokens, r = document.documentElement;
      for (var k in t) r.style.setProperty(k, t[k]);
      refresh();
    }
    if (m.method === "synapse/theme-changed" && m.params?.tokens) {
      var t2 = m.params.tokens, r2 = document.documentElement;
      for (var k2 in t2) r2.style.setProperty(k2, t2[k2]);
    }
  });
  window.parent.postMessage({ jsonrpc: "2.0", method: "ui/ready", params: {} }, "*");
  var inp = document.getElementById("name"), btn = document.getElementById("btn");
  var out = document.getElementById("result"), cnt = document.getElementById("count");
  async function greet() {
    var n = inp.value.trim(); if (!n) return;
    btn.disabled = true; out.textContent = "\\u2026";
    try { out.textContent = text(await callTool("get_greeting", { name: n })); }
    catch (e) { out.textContent = e.message; }
    finally { btn.disabled = false; refresh(); }
  }
  async function refresh() {
    try { cnt.textContent = "Greetings sent: " + text(await callTool("get_greet_count", {})); } catch(_) {}
  }
  btn.onclick = greet;
  inp.onkeydown = function (e) { if (e.key === "Enter") greet(); };
})();
</script>
</body>
</html>
"""
