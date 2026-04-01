#!/usr/bin/env python3
"""
Discord MCP Server using Dedalus MCP.

Uses Discord REST API v9 over HTTPS only (no WebSocket). Base URL:
https://discord.com/api/v9
"""

import asyncio
import logging
import os
import sys

from dotenv import load_dotenv
from dedalus_mcp import MCPServer
from dedalus_mcp.auth import Connection, SecretKeys
from dedalus_mcp.server import TransportSecuritySettings

from src.tools import discord_tools

load_dotenv()

# Connection name "discord" must match ctx.dispatch("discord", ...) in discord_api.py
# auth_header_format must contain "{api_key}" (dedalus_mcp); value is still the bot token.
discord_connection = Connection(
    name="discord",
    secrets=SecretKeys(token="DISCORD_TOKEN"),
    base_url="https://discord.com/api/v9",
    auth_header_format="Bot {api_key}",
)

if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
logger = logging.getLogger(__name__)

as_url = os.getenv("DEDALUS_AS_URL", "https://as.dedaluslabs.ai")

server = MCPServer(
    name="discord-mcp",
    connections=[discord_connection],
    http_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
    streamable_http_stateless=True,
    authorization_server=as_url,
)

server.collect(*discord_tools)
logger.info("Collected %s tools at module level", len(discord_tools))


async def main() -> None:
    """Run the MCP HTTP server (Streamable HTTP + SSE at /mcp)."""
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
    log = logging.getLogger(__name__)
    log.info("Discord MCP Server — auth via Connection 'discord' (ctx.dispatch)")
    port = int(os.getenv("PORT", "8080"))
    host = os.getenv("HOST", "0.0.0.0")
    log.info("Starting on %s:%s", host, port)
    await server.serve(host=host, port=port)


def run() -> None:
    """Console script entry point (`discord-mcp`)."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    log = logging.getLogger(__name__)
    try:
        log.info("Starting Discord MCP Server...")
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Server stopped by user")
    except Exception as e:
        log.error("Failed to start server: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    run()
