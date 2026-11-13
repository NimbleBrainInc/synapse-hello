"""The server answers over the current MCP protocol with FastMCP 4."""

from fastmcp import Client

from mcp_hello.server import mcp


async def test_instructions_reach_the_client():
    async with Client(mcp) as client:
        # client.instructions reads whichever negotiation result the protocol era
        # produced; client.initialize() raises on the modern (server/discover) era.
        assert client.instructions is not None
        assert "get_greeting" in client.instructions


async def test_tools_are_listed():
    async with Client(mcp) as client:
        names = {tool.name for tool in await client.list_tools()}
    assert {"get_greeting", "get_greet_count"} <= names


async def test_greeting_and_count():
    async with Client(mcp) as client:
        greeting = await client.call_tool("get_greeting", {"name": "Ada"})
        count = await client.call_tool("get_greet_count", {})
    assert "Hello, Ada!" in greeting.content[0].text
    assert int(count.content[0].text) >= 1


async def test_ui_resource_is_html():
    async with Client(mcp) as client:
        contents = await client.read_resource("ui://hello/main")
    assert "<html" in contents[0].text.lower()
