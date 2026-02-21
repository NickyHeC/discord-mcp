# client.py
from dedalus_mcp.client import MCPClient
import asyncio

async def main():
    client = await MCPClient.connect("http://127.0.0.1:8000/mcp")
    
    # List available tools
    tools = await client.list_tools()
    print([t.name for t in tools.tools])  # ['add', 'multiply']
    
    # Call a tool
    result = await client.call_tool("add", {"a": 2, "b": 3})
    print(result.content[0].text)  # "5"
    
    await client.close()

asyncio.run(main())