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
    
    # Verify Discord token is set (log warning but don't crash)
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.warning("DISCORD_TOKEN environment variable is not set. Tools will fail when called.")
    else:
        logger.info("DISCORD_TOKEN found")
    
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
