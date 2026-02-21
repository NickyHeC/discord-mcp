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
from dedalus_mcp.auth import Connection, SecretKeys

# Load environment variables from .env file
load_dotenv()

# Define Discord connection for token secret
# Connection name "discord" must match ctx.dispatch("discord", ...) in discord_api.py
discord_connection = Connection(
    name="discord",
    secrets=SecretKeys(token="DISCORD_TOKEN"),
    base_url="https://discord.com/api/v9",
    auth_header_format="Bot {token}",
)

# Handle imports for both package and direct execution
# Set up logging first to capture import errors
import logging
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger(__name__)

try:
    from .tools import discord_tools
    logger.debug("Imported discord_tools using relative import")
except ImportError as e:
    # Fallback for direct execution or when package structure differs
    logger.debug(f"Relative import failed: {e}, trying absolute import")
    src_path = Path(__file__).parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    try:
        from tools import discord_tools
        logger.debug("Imported discord_tools using absolute import")
    except ImportError as e2:
        logger.error(f"Failed to import discord_tools: {e2}")
        raise

# --- Server ---

server = MCPServer(
    name="discord-mcp",
    connections=[discord_connection],
    authorization_server=os.getenv("DEDALUS_AS_URL", "https://as.dedaluslabs.ai"),
    streamable_http_stateless=True,
)

# Collect tools at module level (required for Dedalus deployment)

try:
    server.collect(*discord_tools)
    logger.info(f"Successfully collected {len(discord_tools)} tools at module level")
except Exception as e:
    logger.error(f"Error collecting tools: {e}", exc_info=True)
    raise


async def main() -> None:
    """Main entry point for the MCP server."""
    import logging
    
    # Set up logging (in case it wasn't set up already)
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    logger = logging.getLogger(__name__)
    
    logger.info("Initializing Discord MCP Server...")
    
    # Note: Authentication is handled automatically by Dedalus via ctx.dispatch
    # The token is injected by the framework based on the Connection definition
    logger.info("Discord authentication handled via Dedalus dispatch (Connection: 'discord')")
    logger.info(f"Collected {len(discord_tools)} tools")
    
    # Get port from environment or use default
    port = int(os.getenv("PORT", "8080"))
    # Bind to 0.0.0.0 so deployment/validation can reach /mcp from outside the container
    host = os.getenv("HOST", "0.0.0.0")

    # Serve the MCP server (HTTP/SSE at /mcp)
    logger.info(f"Starting Discord MCP Server on {host}:{port}")
    await server.serve(host=host, port=port)


def run() -> None:
    """Sync entry point for console script (e.g. discord-mcp). Runs the async server."""
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    _logger = logging.getLogger(__name__)
    try:
        _logger.info("Starting Discord MCP Server...")
        asyncio.run(main())
    except KeyboardInterrupt:
        _logger.info("Server stopped by user")
    except Exception as e:
        _logger.error(f"Failed to start server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    run()
