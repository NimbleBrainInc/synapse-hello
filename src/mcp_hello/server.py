"""Hello World MCP App — FastMCP server with tools and UI resource."""

import sys

from fastmcp import FastMCP

from .ui import load_ui

mcp = FastMCP(
    "Hello",
    instructions="A minimal Hello World MCP App. Call get_greeting to greet someone by name.",
)

# Session state
_greet_count: int = 0


@mcp.tool()
async def get_greeting(name: str) -> str:
    """Greet someone by name.

    Args:
        name: The person to greet.
    """
    global _greet_count
    _greet_count += 1
    return f"Hello, {name}! 👋"


@mcp.tool()
async def get_greet_count() -> str:
    """Get the number of greetings sent this session."""
    return str(_greet_count)


@mcp.resource("ui://hello/main")
def hello_ui() -> str:
    """The Hello World app UI — rendered in the platform sidebar."""
    return load_ui()


# ASGI entrypoint for HTTP deployment
app = mcp.http_app()

# Stdio entrypoint for mpak / Claude Desktop
if __name__ == "__main__":
    print("Hello MCP App starting in stdio mode…", file=sys.stderr)
    mcp.run()
