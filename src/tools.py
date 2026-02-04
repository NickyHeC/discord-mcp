# tools.py - Discord tools using Discord API v9
import asyncio
import sys
from pathlib import Path
from typing import List, Optional
from dedalus_mcp import tool
from pydantic import BaseModel

# Handle imports for both package and direct execution
try:
    from .discord_api import (
        send_message_v9,
        get_channel_messages_v9,
        get_guild_v9,
        get_guild_channels_v9,
        get_current_user_guilds_v9,
        delete_message_v9,
        create_reaction_v9,
        get_user_v9,
        get_guild_members_v9,
    )
except ImportError:
    # Fallback for direct execution or when package structure differs
    src_path = Path(__file__).parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    from discord_api import (
        send_message_v9,
        get_channel_messages_v9,
        get_guild_v9,
        get_guild_channels_v9,
        get_current_user_guilds_v9,
        delete_message_v9,
        create_reaction_v9,
        get_user_v9,
        get_guild_members_v9,
    )


class MessageResponse(BaseModel):
    id: str
    author: str
    content: str
    timestamp: Optional[str] = None
    attachments: int = 0


class MessagesResponse(BaseModel):
    count: int
    messages: List[MessageResponse]


class ServerInfo(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    member_count: Optional[int] = None
    owner_id: Optional[str] = None
    icon_url: Optional[str] = None
    features: List[str] = []
    verification_level: Optional[int] = None
    premium_tier: Optional[int] = None


class ChannelInfo(BaseModel):
    id: str
    name: str
    type: int
    position: Optional[int] = None
    parent_id: Optional[str] = None


class ChannelsResponse(BaseModel):
    count: int
    channels: List[ChannelInfo]
    error: Optional[str] = None


class MemberInfo(BaseModel):
    id: str
    username: str
    discriminator: str
    global_name: Optional[str] = None
    bot: bool = False
    joined_at: Optional[str] = None


class MembersResponse(BaseModel):
    count: int
    members: List[MemberInfo]


class UserInfo(BaseModel):
    id: str
    username: str
    discriminator: str
    global_name: Optional[str] = None
    bot: bool = False
    avatar_url: Optional[str] = None


class SendMessageResponse(BaseModel):
    success: bool
    message_id: str


class ActionResponse(BaseModel):
    success: bool
    message: str


@tool(description="Send a message to a Discord channel.")
async def send_message(channel_id: str, content: str) -> SendMessageResponse:
    try:
        result = await send_message_v9(channel_id, content)
        if not isinstance(result, dict):
            raise ValueError(f"Unexpected response type: {type(result)}")
        return SendMessageResponse(
            success=True,
            message_id=result.get("id", "unknown")
        )
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg or "Missing Access" in error_msg:
            raise ValueError(f"Missing permissions to send messages in channel {channel_id}. The bot needs 'Send Messages' permission.")
        elif "404" in error_msg:
            raise ValueError(f"Channel {channel_id} not found.")
        else:
            raise ValueError(f"Failed to send message: {error_msg}")


@tool(description="Read recent messages from a Discord channel. Requires messages.read scope.")
async def read_messages(channel_id: str, limit: int = 50) -> MessagesResponse:
    try:
        limit = min(limit, 100)
        messages = await get_channel_messages_v9(channel_id, limit=limit)
        
        if not isinstance(messages, list):
            raise ValueError(f"Expected list of messages, got {type(messages)}")
        
        formatted_messages = []
        for msg in messages:
            if not isinstance(msg, dict):
                continue
            author = msg.get("author", {})
            formatted_messages.append(MessageResponse(
                id=msg.get("id", ""),
                author=f"{author.get('username', 'Unknown')}#{author.get('discriminator', '0000')}",
                content=msg.get("content", ""),
                timestamp=msg.get("timestamp"),
                attachments=len(msg.get("attachments", []))
            ))
        
        return MessagesResponse(
            count=len(formatted_messages),
            messages=formatted_messages
        )
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg or "Missing Access" in error_msg:
            raise ValueError(f"Missing permissions to read messages in channel {channel_id}. The bot needs 'Read Message History' permission and 'messages.read' scope.")
        elif "404" in error_msg:
            raise ValueError(f"Channel {channel_id} not found.")
        else:
            raise ValueError(f"Failed to read messages: {error_msg}")


@tool(description="List all Discord servers (guilds) the bot is in.")
async def list_servers() -> List[dict]:
    try:
        guilds = await get_current_user_guilds_v9(limit=200)
        
        if not isinstance(guilds, list):
            raise ValueError(f"Expected list of guilds, got {type(guilds)}")
        
        servers = []
        for guild in guilds:
            if not isinstance(guild, dict):
                continue
            servers.append({
                "id": guild.get("id"),
                "name": guild.get("name"),
                "icon": guild.get("icon"),
                "owner": guild.get("owner", False),
                "permissions": guild.get("permissions")
            })
        
        return servers
    except Exception as e:
        error_msg = str(e)
        raise ValueError(f"Failed to list servers: {error_msg}")


@tool(description="Get detailed information about a Discord server.")
async def get_server_info(server_id: str) -> ServerInfo:
    try:
        guild = await get_guild_v9(server_id)
        
        if not isinstance(guild, dict):
            raise ValueError(f"Expected dict for guild info, got {type(guild)}")
        
        return ServerInfo(
            id=guild.get("id", ""),
            name=guild.get("name", ""),
            description=guild.get("description"),
            member_count=guild.get("approximate_member_count"),
            owner_id=guild.get("owner_id"),
            icon_url=f"https://cdn.discordapp.com/icons/{guild.get('id')}/{guild.get('icon')}.png" if guild.get("icon") else None,
            features=guild.get("features", []),
            verification_level=guild.get("verification_level"),
            premium_tier=guild.get("premium_tier")
        )
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg or "Missing Access" in error_msg:
            raise ValueError(f"Missing permissions to access server {server_id}. The bot may not be a member of this server.")
        elif "404" in error_msg or "Unknown Guild" in error_msg:
            raise ValueError(f"Server {server_id} not found.")
        else:
            raise ValueError(f"Failed to get server info: {error_msg}")


@tool(description="List all channels in a Discord server. Requires guilds.channels.read scope.")
async def list_channels(server_id: str) -> dict:
    """
    Returns a dict with:
    - count: int - number of channels
    - channels: list[dict] - list of channel objects, each with: id (str), name (str), type (int), position (int or None), parent_id (str or None)
    - error: str or None - error message if something went wrong
    """
    try:
        channels = await get_guild_channels_v9(server_id)
        
        # Ensure channels is a list
        if not isinstance(channels, list):
            return {
                "count": 0,
                "channels": [],
                "error": f"Expected list of channels, got {type(channels)}: {channels}"
            }
        
        # Format channels as plain dicts (no nested Pydantic models)
        formatted_channels = []
        for channel in channels:
            if not isinstance(channel, dict):
                continue
            # Create flat dict with only primitives, omit None values
            channel_dict = {
                "id": str(channel.get("id", "")),
                "name": str(channel.get("name", "")),
                "type": int(channel.get("type", 0))
            }
            # Only include optional fields if they have values
            if channel.get("position") is not None:
                channel_dict["position"] = int(channel.get("position"))
            if channel.get("parent_id"):
                channel_dict["parent_id"] = str(channel.get("parent_id"))
            formatted_channels.append(channel_dict)
        
        return {
            "count": len(formatted_channels),
            "channels": formatted_channels
        }
    except Exception as e:
        error_msg = str(e)
        error_detail = ""
        if "403" in error_msg or "Missing Access" in error_msg or "Missing Permissions" in error_msg:
            error_detail = f"Permission denied (403) for server {server_id}. The bot needs 'View Channels' permission in the server. To fix: 1) Go to Server Settings > Roles > [Bot Role] and enable 'View Channels', or 2) Re-invite the bot with 'View Channels' permission. Error details: {error_msg}"
        elif "404" in error_msg or "Unknown Guild" in error_msg:
            error_detail = f"Server {server_id} not found (404). The bot may not be a member of this server. Verify the server_id is correct and the bot has been invited. Error details: {error_msg}"
        elif "401" in error_msg or "Unauthorized" in error_msg:
            error_detail = f"Authentication failed (401) for server {server_id}. The DISCORD_TOKEN may be invalid, expired, or not properly configured in the hosted MCP server environment. Error details: {error_msg}"
        else:
            error_detail = f"Failed to list channels for server {server_id}. Error: {error_msg}"
        
        return {
            "count": 0,
            "channels": [],
            "error": error_detail
        }


@tool(description="Add a reaction emoji to a message.")
async def add_reaction(channel_id: str, message_id: str, emoji: str) -> ActionResponse:
    try:
        await create_reaction_v9(channel_id, message_id, emoji)
        return ActionResponse(
            success=True,
            message=f"Reaction '{emoji}' added successfully!"
        )
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg or "Missing Access" in error_msg:
            raise ValueError(f"Missing permissions to add reactions in channel {channel_id}.")
        elif "404" in error_msg:
            raise ValueError(f"Channel {channel_id} or message {message_id} not found.")
        else:
            raise ValueError(f"Failed to add reaction: {error_msg}")


@tool(description="Delete a message from a Discord channel.")
async def delete_message(channel_id: str, message_id: str) -> ActionResponse:
    try:
        await delete_message_v9(channel_id, message_id)
        return ActionResponse(
            success=True,
            message=f"Message {message_id} deleted successfully!"
        )
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg or "Missing Access" in error_msg:
            raise ValueError(f"Missing permissions to delete messages in channel {channel_id}. The bot needs 'Manage Messages' permission.")
        elif "404" in error_msg:
            raise ValueError(f"Channel {channel_id} or message {message_id} not found.")
        else:
            raise ValueError(f"Failed to delete message: {error_msg}")


@tool(description="Get information about a Discord user.")
async def get_user_info(user_id: str) -> UserInfo:
    try:
        user = await get_user_v9(user_id)
        
        if not isinstance(user, dict):
            raise ValueError(f"Expected dict for user info, got {type(user)}")
        
        return UserInfo(
            id=user.get("id", ""),
            username=user.get("username", ""),
            discriminator=user.get("discriminator", "0000"),
            global_name=user.get("global_name"),
            bot=user.get("bot", False),
            avatar_url=f"https://cdn.discordapp.com/avatars/{user.get('id')}/{user.get('avatar')}.png" if user.get("avatar") else None
        )
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
            raise ValueError(f"User {user_id} not found.")
        else:
            raise ValueError(f"Failed to get user info: {error_msg}")


@tool(description="List members in a Discord server. Requires guilds.members.read scope.")
async def list_members(server_id: str, limit: int = 100) -> MembersResponse:
    try:
        limit = min(limit, 1000)
        members = await get_guild_members_v9(server_id, limit=limit)
        
        if not isinstance(members, list):
            raise ValueError(f"Expected list of members, got {type(members)}")
        
        formatted_members = []
        for member in members:
            if not isinstance(member, dict):
                continue
            user = member.get("user", {})
            formatted_members.append(MemberInfo(
                id=user.get("id", ""),
                username=user.get("username", ""),
                discriminator=user.get("discriminator", "0000"),
                global_name=user.get("global_name"),
                bot=user.get("bot", False),
                joined_at=member.get("joined_at")
            ))
        
        return MembersResponse(
            count=len(formatted_members),
            members=formatted_members
        )
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg or "Missing Access" in error_msg:
            raise ValueError(f"Missing permissions to list members in server {server_id}. The bot needs 'guilds.members.read' scope and appropriate permissions.")
        elif "404" in error_msg:
            raise ValueError(f"Server {server_id} not found.")
        else:
            raise ValueError(f"Failed to list members: {error_msg}")


discord_tools = [
    send_message,
    read_messages,
    list_servers,
    get_server_info,
    list_channels,
    add_reaction,
    delete_message,
    get_user_info,
    list_members,
]
