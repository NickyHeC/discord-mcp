"""Local test client for the Discord MCP server.

1) Test DAuth Connection + token (no running server):
       python -m src.client --test-connection

2) Call tools against a running server:
       python -m src.main   # other terminal
       python -m src.client

   Optional: MCP_URL=http://127.0.0.1:8080/mcp
"""

import asyncio
import os
import sys

from dotenv import load_dotenv

load_dotenv()

DEFAULT_MCP_URL = "http://127.0.0.1:8080/mcp"


async def test_connection() -> None:
    """Verify Connection config and DISCORD_TOKEN against Discord API."""
    from dedalus_mcp.testing import ConnectionTester, TestRequest

    from src.main import discord_connection

    tester = ConnectionTester.from_env(discord_connection)
    response = await tester.request(TestRequest(path="/users/@me"))

    if response.success:
        print(f"OK {response.status} — Connection works!")
        print(f"Response: {response.body}")
    else:
        print(f"FAIL {response.status}")
        print(f"Response: {response.body}")


async def test_tools() -> None:
    """Connect to the running server and exercise tools."""
    from dedalus_mcp.client import MCPClient

    url = os.getenv("MCP_URL", DEFAULT_MCP_URL)
    print(f"Connecting to {url} ...")

    client = await MCPClient.connect(url)

    tools = await client.list_tools()
    names = [t.name for t in tools.tools]
    print("Tools:", names)

    if "list_servers" in names:
        result = await client.call_tool("list_servers", {})
        if result.content:
            text = result.content[0].text
            preview = text[:200] + "..." if len(text) > 200 else text
            print("list_servers result:", preview)
        else:
            print("list_servers result: (empty)")
    else:
        print("(Skipping tool call; list_servers not found)")

    await client.close()
    print("Done.")


if __name__ == "__main__":
    if "--test-connection" in sys.argv:
        asyncio.run(test_connection())
    else:
        asyncio.run(test_tools())
