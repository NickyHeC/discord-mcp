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
    import logging
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Read Discord app configuration from local .env file
    DISCORD_APP_ID = os.getenv("DISCORD_APP_ID")
    DISCORD_PUBLIC_KEY = os.getenv("DISCORD_PUBLIC_KEY")
    
    if not DISCORD_APP_ID or not DISCORD_PUBLIC_KEY:
        raise RuntimeError("Missing Discord app configuration. DISCORD_APP_ID and DISCORD_PUBLIC_KEY must be set in .env file.")
    
    logger.info("Discord app configuration loaded from .env file")
    
    # Note: DISCORD_TOKEN is accessed via ctx.secrets["token"] in tools, not from environment variables
    logger.info("Discord token will be accessed via ctx.secrets['token'] when tools are called")
    
    # Collect all tools
    try:
        server.collect(*discord_tools)
        logger.info(f"Collected {len(discord_tools)} tools")
    except Exception as e:
        logger.error(f"Error collecting tools: {e}", exc_info=True)
        raise
    
    # Get port from environment or use default
    port = int(os.getenv("PORT", "8080"))
    
    # Serve the MCP server
    logger.info(f"Starting Discord MCP Server on port {port}")
    await server.serve(port=port)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        import logging
        logging.basicConfig(level=logging.ERROR)
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to start server: {e}", exc_info=True)
        raise
