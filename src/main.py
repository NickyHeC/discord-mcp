#!/usr/bin/env python3
"""
Discord MCP Server using Dedalus MCP Framework

This server uses Discord REST API version 9 (v9) exclusively via HTTPS.
Base URL: https://discord.com/api/v9

All operations use HTTPS REST API calls - no WebSocket connections.
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from dedalus_mcp import MCPServer

# Load environment variables from .env file
load_dotenv()

# Handle imports for both package and direct execution
try:
    from .tools import discord_tools
except ImportError:
    # Fallback for direct execution or when package structure differs
    src_path = Path(__file__).parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    from tools import discord_tools

# --- Server ---

server = MCPServer(name="discord-mcp")


async def main() -> None:
    """Main entry point for the MCP server."""
    # Verify Discord token is set
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("DISCORD_TOKEN environment variable is required. Set it in .env file.")
    
    # Collect all tools
    server.collect(*discord_tools)
    
    # Get port from environment or use default
    port = int(os.getenv("PORT", "8080"))
    
    # Serve the MCP server
    await server.serve(port=port)
    print(f"Discord MCP Server running on port {port}")


if __name__ == "__main__":
    asyncio.run(main())
