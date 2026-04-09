import { useState } from "react";
import {
  SynapseProvider,
  useCallTool,
  useDataSync,
  useTheme,
} from "@nimblebrain/synapse/react";

function HelloApp() {
  const [name, setName] = useState("");
  const [greeting, setGreeting] = useState("Type a name and click Greet.");
  const [error, setError] = useState<string | null>(null);
  const [count, setCount] = useState<number | null>(null);

  const greetTool = useCallTool<string>("get_greeting");
  const countTool = useCallTool<string>("get_greet_count");
  const theme = useTheme();

  // Refresh count when the agent calls our tools
  useDataSync(() => {
    refreshCount();
  });

  async function refreshCount() {
    try {
      const result = await countTool.call({});
      setCount(Number(result.data));
    } catch {
      // non-critical
    }
  }

  async function greet() {
    const trimmed = name.trim();
    if (!trimmed) return;

    setError(null);
    setGreeting("\u2026");

    try {
      const result = await greetTool.call({ name: trimmed });
      setGreeting(String(result.data));
      refreshCount();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      setGreeting("");
    }
  }

  return (
    <div style={styles.container}>
      <h1 style={styles.heading}>Hello 👋</h1>

      <div style={styles.inputRow}>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && greet()}
          placeholder="Enter a name…"
          autoFocus
          style={{
            ...styles.input,
            borderColor: theme.tokens["--color-border-primary"] || "#e5e7eb",
            background: theme.tokens["--color-background-secondary"] || "#f9fafb",
          }}
        />
        <button
          onClick={greet}
          disabled={greetTool.isPending}
          style={{
            ...styles.button,
            background: theme.tokens["--color-text-accent"] || "#2563eb",
            opacity: greetTool.isPending ? 0.5 : 1,
          }}
        >
          Greet
        </button>
      </div>

      <div
        style={{
          ...styles.result,
          borderColor: theme.tokens["--color-border-primary"] || "#e5e7eb",
          background: theme.tokens["--color-background-secondary"] || "#f9fafb",
        }}
      >
        {error ? (
          <span style={{ color: theme.tokens["--nb-color-danger"] || "#ef4444" }}>
            {error}
          </span>
        ) : (
          greeting
        )}
      </div>

      {count !== null && (
        <div
          style={{
            ...styles.count,
            color: theme.tokens["--color-text-secondary"] || "#6b7280",
          }}
        >
          Greetings sent: {count}
        </div>
      )}
    </div>
  );
}

export function App() {
  return (
    <SynapseProvider name="hello" version="0.1.0">
      <HelloApp />
    </SynapseProvider>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    maxWidth: 420,
    width: "100%",
    margin: "0 auto",
    padding: "2rem",
    fontFamily:
      "var(--font-sans, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif)",
  },
  heading: {
    fontSize: "1.5rem",
    marginBottom: "1.5rem",
  },
  inputRow: {
    display: "flex",
    gap: "0.5rem",
    marginBottom: "1rem",
  },
  input: {
    flex: 1,
    padding: "0.6rem 0.75rem",
    borderRadius: 6,
    border: "1px solid",
    fontSize: "0.95rem",
    outline: "none",
  },
  button: {
    padding: "0.6rem 1.25rem",
    borderRadius: 6,
    border: "none",
    color: "#fff",
    fontSize: "0.95rem",
    cursor: "pointer",
    fontWeight: 500,
    whiteSpace: "nowrap",
  },
  result: {
    marginTop: "1rem",
    padding: "1rem",
    borderRadius: 8,
    border: "1px solid",
    fontSize: "1.1rem",
    minHeight: "3rem",
    display: "flex",
    alignItems: "center",
  },
  count: {
    marginTop: "0.75rem",
    fontSize: "0.85rem",
  },
};
