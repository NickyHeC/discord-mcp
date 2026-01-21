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
    result = await send_message_v9(channel_id, content)
    return SendMessageResponse(
        success=True,
        message_id=result.get("id", "unknown")
    )


@tool(description="Read recent messages from a Discord channel. Requires messages.read scope.")
async def read_messages(channel_id: str, limit: int = 50) -> MessagesResponse:
    limit = min(limit, 100)
    messages = await get_channel_messages_v9(channel_id, limit=limit)
    
    formatted_messages = []
    for msg in messages:
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


@tool(description="List all Discord servers (guilds) the bot is in.")
async def list_servers() -> List[dict]:
    guilds = await get_current_user_guilds_v9(limit=200)
    
    servers = []
    for guild in guilds:
        servers.append({
            "id": guild.get("id"),
            "name": guild.get("name"),
            "icon": guild.get("icon"),
            "owner": guild.get("owner", False),
            "permissions": guild.get("permissions")
        })
    
    return servers


@tool(description="Get detailed information about a Discord server.")
async def get_server_info(server_id: str) -> ServerInfo:
    guild = await get_guild_v9(server_id)
    
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


@tool(description="List all channels in a Discord server. Requires guilds.channels.read scope.")
async def list_channels(server_id: str) -> ChannelsResponse:
    channels = await get_guild_channels_v9(server_id)
    
    formatted_channels = []
    for channel in channels:
        formatted_channels.append(ChannelInfo(
            id=channel.get("id", ""),
            name=channel.get("name", ""),
            type=channel.get("type", 0),
            position=channel.get("position"),
            parent_id=channel.get("parent_id")
        ))
    
    return ChannelsResponse(
        count=len(formatted_channels),
        channels=formatted_channels
    )


@tool(description="Add a reaction emoji to a message.")
async def add_reaction(channel_id: str, message_id: str, emoji: str) -> ActionResponse:
    await create_reaction_v9(channel_id, message_id, emoji)
    return ActionResponse(
        success=True,
        message=f"Reaction '{emoji}' added successfully!"
    )


@tool(description="Delete a message from a Discord channel.")
async def delete_message(channel_id: str, message_id: str) -> ActionResponse:
    await delete_message_v9(channel_id, message_id)
    return ActionResponse(
        success=True,
        message=f"Message {message_id} deleted successfully!"
    )


@tool(description="Get information about a Discord user.")
async def get_user_info(user_id: str) -> UserInfo:
    user = await get_user_v9(user_id)
    
    return UserInfo(
        id=user.get("id", ""),
        username=user.get("username", ""),
        discriminator=user.get("discriminator", "0000"),
        global_name=user.get("global_name"),
        bot=user.get("bot", False),
        avatar_url=f"https://cdn.discordapp.com/avatars/{user.get('id')}/{user.get('avatar')}.png" if user.get("avatar") else None
    )


@tool(description="List members in a Discord server. Requires guilds.members.read scope.")
async def list_members(server_id: str, limit: int = 100) -> MembersResponse:
    limit = min(limit, 1000)
    members = await get_guild_members_v9(server_id, limit=limit)
    
    formatted_members = []
    for member in members:
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
