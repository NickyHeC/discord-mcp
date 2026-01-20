#!/usr/bin/env python3
"""
Discord MCP Server
A Model Context Protocol server for interacting with Discord.
"""

import os
import asyncio
import json
from typing import Any, Optional

import discord
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Initialize Discord bot client
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.presences = True

bot_client: Optional[discord.Client] = None

# Initialize MCP server
mcp_server = Server("discord-mcp")


async def get_bot_client() -> discord.Client:
    """Get the Discord bot client."""
    global bot_client
    if bot_client is None:
        raise RuntimeError("Discord bot client not initialized. Call main() first.")
    
    if not bot_client.is_ready():
        await bot_client.wait_until_ready()
    
    return bot_client


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available Discord tools."""
    return [
        Tool(
            name="send_message",
            description="Send a message to a Discord channel",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "The Discord channel ID to send the message to"
                    },
                    "content": {
                        "type": "string",
                        "description": "The message content to send"
                    }
                },
                "required": ["channel_id", "content"]
            }
        ),
        Tool(
            name="read_messages",
            description="Read recent messages from a Discord channel",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "The Discord channel ID to read messages from"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of messages to retrieve (default: 50, max: 100)",
                        "default": 50
                    }
                },
                "required": ["channel_id"]
            }
        ),
        Tool(
            name="list_servers",
            description="List all Discord servers (guilds) the bot is in",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_server_info",
            description="Get detailed information about a Discord server",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_id": {
                        "type": "string",
                        "description": "The Discord server (guild) ID"
                    }
                },
                "required": ["server_id"]
            }
        ),
        Tool(
            name="list_channels",
            description="List all channels in a Discord server",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_id": {
                        "type": "string",
                        "description": "The Discord server (guild) ID"
                    }
                },
                "required": ["server_id"]
            }
        ),
        Tool(
            name="add_reaction",
            description="Add a reaction emoji to a message",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "The Discord channel ID where the message is"
                    },
                    "message_id": {
                        "type": "string",
                        "description": "The Discord message ID to react to"
                    },
                    "emoji": {
                        "type": "string",
                        "description": "The emoji to add (e.g., '👍', '❤️', or custom emoji name)"
                    }
                },
                "required": ["channel_id", "message_id", "emoji"]
            }
        ),
        Tool(
            name="delete_message",
            description="Delete a message from a Discord channel",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "The Discord channel ID where the message is"
                    },
                    "message_id": {
                        "type": "string",
                        "description": "The Discord message ID to delete"
                    }
                },
                "required": ["channel_id", "message_id"]
            }
        ),
        Tool(
            name="get_user_info",
            description="Get information about a Discord user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The Discord user ID"
                    }
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="list_members",
            description="List members in a Discord server",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_id": {
                        "type": "string",
                        "description": "The Discord server (guild) ID"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of members to retrieve (default: 100)",
                        "default": 100
                    }
                },
                "required": ["server_id"]
            }
        ),
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    client = await get_bot_client()
    
    try:
        if name == "send_message":
            channel_id = int(arguments["channel_id"])
            content = arguments["content"]
            channel = client.get_channel(channel_id)
            
            if not channel:
                return [TextContent(
                    type="text",
                    text=f"Error: Channel {channel_id} not found"
                )]
            
            message = await channel.send(content)
            return [TextContent(
                type="text",
                text=f"Message sent successfully! Message ID: {message.id}"
            )]
        
        elif name == "read_messages":
            channel_id = int(arguments["channel_id"])
            limit = min(arguments.get("limit", 50), 100)
            channel = client.get_channel(channel_id)
            
            if not channel:
                return [TextContent(
                    type="text",
                    text=f"Error: Channel {channel_id} not found"
                )]
            
            messages = []
            async for message in channel.history(limit=limit):
                messages.append({
                    "id": str(message.id),
                    "author": str(message.author),
                    "content": message.content,
                    "timestamp": message.created_at.isoformat(),
                    "attachments": len(message.attachments)
                })
            
            return [TextContent(
                type="text",
                text=f"Retrieved {len(messages)} messages:\n{json.dumps(messages, indent=2)}"
            )]
        
        elif name == "list_servers":
            servers = []
            for guild in client.guilds:
                servers.append({
                    "id": str(guild.id),
                    "name": guild.name,
                    "member_count": guild.member_count,
                    "owner_id": str(guild.owner_id) if guild.owner else None
                })
            
            return [TextContent(
                type="text",
                text=f"Bot is in {len(servers)} servers:\n{json.dumps(servers, indent=2)}"
            )]
        
        elif name == "get_server_info":
            server_id = int(arguments["server_id"])
            guild = client.get_guild(server_id)
            
            if not guild:
                return [TextContent(
                    type="text",
                    text=f"Error: Server {server_id} not found"
                )]
            
            server_info = {
                "id": str(guild.id),
                "name": guild.name,
                "description": guild.description,
                "member_count": guild.member_count,
                "owner_id": str(guild.owner_id) if guild.owner else None,
                "created_at": guild.created_at.isoformat() if guild.created_at else None,
                "icon_url": str(guild.icon.url) if guild.icon else None,
                "channel_count": len(guild.channels),
                "role_count": len(guild.roles)
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(server_info, indent=2)
            )]
        
        elif name == "list_channels":
            server_id = int(arguments["server_id"])
            guild = client.get_guild(server_id)
            
            if not guild:
                return [TextContent(
                    type="text",
                    text=f"Error: Server {server_id} not found"
                )]
            
            channels = []
            for channel in guild.channels:
                channels.append({
                    "id": str(channel.id),
                    "name": channel.name,
                    "type": str(channel.type),
                    "category": channel.category.name if channel.category else None
                })
            
            return [TextContent(
                type="text",
                text=f"Found {len(channels)} channels:\n{json.dumps(channels, indent=2)}"
            )]
        
        elif name == "add_reaction":
            channel_id = int(arguments["channel_id"])
            message_id = int(arguments["message_id"])
            emoji = arguments["emoji"]
            
            channel = client.get_channel(channel_id)
            if not channel:
                return [TextContent(
                    type="text",
                    text=f"Error: Channel {channel_id} not found"
                )]
            
            message = await channel.fetch_message(message_id)
            await message.add_reaction(emoji)
            
            return [TextContent(
                type="text",
                text=f"Reaction '{emoji}' added successfully!"
            )]
        
        elif name == "delete_message":
            channel_id = int(arguments["channel_id"])
            message_id = int(arguments["message_id"])
            
            channel = client.get_channel(channel_id)
            if not channel:
                return [TextContent(
                    type="text",
                    text=f"Error: Channel {channel_id} not found"
                )]
            
            message = await channel.fetch_message(message_id)
            await message.delete()
            
            return [TextContent(
                type="text",
                text=f"Message {message_id} deleted successfully!"
            )]
        
        elif name == "get_user_info":
            user_id = int(arguments["user_id"])
            user = await client.fetch_user(user_id)
            
            user_info = {
                "id": str(user.id),
                "name": user.name,
                "display_name": user.display_name,
                "discriminator": user.discriminator,
                "bot": user.bot,
                "avatar_url": str(user.display_avatar.url) if user.display_avatar else None,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(user_info, indent=2)
            )]
        
        elif name == "list_members":
            server_id = int(arguments["server_id"])
            limit = min(arguments.get("limit", 100), 1000)
            guild = client.get_guild(server_id)
            
            if not guild:
                return [TextContent(
                    type="text",
                    text=f"Error: Server {server_id} not found"
                )]
            
            # Ensure members are cached
            if not guild.chunked:
                await guild.chunk()
            
            members = []
            for member in list(guild.members)[:limit]:
                members.append({
                    "id": str(member.id),
                    "name": member.name,
                    "display_name": member.display_name,
                    "bot": member.bot,
                    "joined_at": member.joined_at.isoformat() if member.joined_at else None
                })
            
            return [TextContent(
                type="text",
                text=f"Retrieved {len(members)} members:\n{json.dumps(members, indent=2)}"
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"Error: Unknown tool '{name}'"
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def main():
    """Main entry point for the MCP server."""
    # Start Discord bot connection in background
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("DISCORD_TOKEN environment variable is required")
    
    # Initialize bot client
    global bot_client
    bot_client = discord.Client(intents=intents)
    
    # Start bot connection
    async def start_bot():
        try:
            await bot_client.start(token)
        except Exception as e:
            print(f"Error starting Discord bot: {e}", file=os.sys.stderr)
    
    # Start bot in background task
    bot_task = asyncio.create_task(start_bot())
    
    # Wait for bot to be ready
    try:
        await asyncio.wait_for(bot_client.wait_until_ready(), timeout=30.0)
    except asyncio.TimeoutError:
        raise RuntimeError("Discord bot failed to connect within 30 seconds")
    
    # Run MCP server over stdio
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
