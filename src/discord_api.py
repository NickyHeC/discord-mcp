"""
Discord REST API v9 client utilities.
Provides direct HTTP access to Discord API version 9.
"""

import os
import ssl
import certifi
import aiohttp
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Discord API Configuration
DISCORD_API_BASE_URL = "https://discord.com/api/v9"
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_APP_ID = os.getenv("APP_ID")


async def discord_api_request(
    method: str,
    endpoint: str,
    token: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Make a request to Discord REST API v9.
    
    According to Discord API reference:
    - All requests must use HTTPS (TLS 1.2+)
    - Authorization header format: "Bot {token}"
    - User-Agent should identify the bot
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE, PATCH)
        endpoint: API endpoint (e.g., '/channels/{channel_id}/messages')
        token: Discord bot token (defaults to DISCORD_TOKEN env var)
        data: Request body data (will be JSON encoded)
        params: URL query parameters
    
    Returns:
        JSON response as dictionary
    
    Raises:
        ValueError: If token is missing
        aiohttp.ClientResponseError: For HTTP errors
    """
    token = token or DISCORD_TOKEN
    if not token:
        raise ValueError("DISCORD_TOKEN environment variable is required. Set it in .env file.")
    
    # Strip any whitespace from token (common .env mistake)
    token = token.strip()
    
    url = f"{DISCORD_API_BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json",
        "User-Agent": "DiscordBot (discord-mcp, 0.1.0)",
    }
    
    # Create SSL context with certifi certificates
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.request(
            method=method,
            url=url,
            headers=headers,
            json=data,
            params=params,
        ) as response:
            # Raise exception for HTTP errors
            if response.status >= 400:
                error_text = await response.text()
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message=f"Discord API error: {error_text}"
                )
            
            # Handle empty responses (e.g., 204 No Content)
            if response.content_length == 0 or response.status == 204:
                return {}
            
            try:
                return await response.json()
            except aiohttp.ContentTypeError:
                # Some endpoints may return non-JSON responses
                return {"raw": await response.text()}


async def send_message_v9(channel_id: str, content: str) -> Dict[str, Any]:
    """Send a message using Discord API v9."""
    return await discord_api_request(
        "POST",
        f"/channels/{channel_id}/messages",
        data={"content": content},
    )


async def get_channel_messages_v9(
    channel_id: str,
    limit: int = 50,
    before: Optional[str] = None,
    after: Optional[str] = None,
) -> list[Dict[str, Any]]:
    """Get channel messages using Discord API v9."""
    params = {"limit": min(limit, 100)}
    if before:
        params["before"] = before
    if after:
        params["after"] = after
    
    result = await discord_api_request(
        "GET",
        f"/channels/{channel_id}/messages",
        params=params,
    )
    # Ensure we return a list
    if not isinstance(result, list):
        raise ValueError(f"Expected list of messages, got {type(result)}: {result}")
    return result


async def get_guild_v9(guild_id: str) -> Dict[str, Any]:
    """Get guild information using Discord API v9."""
    return await discord_api_request("GET", f"/guilds/{guild_id}")


async def get_guild_channels_v9(guild_id: str) -> list[Dict[str, Any]]:
    """Get guild channels using Discord API v9."""
    result = await discord_api_request("GET", f"/guilds/{guild_id}/channels")
    # Ensure we return a list
    if not isinstance(result, list):
        raise ValueError(f"Expected list of channels, got {type(result)}: {result}")
    return result


async def get_current_user_guilds_v9(limit: int = 200) -> list[Dict[str, Any]]:
    """Get current user's guilds using Discord API v9."""
    params = {"limit": min(limit, 200)}
    result = await discord_api_request("GET", "/users/@me/guilds", params=params)
    # Ensure we return a list
    if not isinstance(result, list):
        raise ValueError(f"Expected list of guilds, got {type(result)}: {result}")
    return result


async def delete_message_v9(channel_id: str, message_id: str) -> None:
    """Delete a message using Discord API v9."""
    await discord_api_request(
        "DELETE",
        f"/channels/{channel_id}/messages/{message_id}",
    )


async def create_reaction_v9(
    channel_id: str,
    message_id: str,
    emoji: str,
) -> None:
    """Create a reaction using Discord API v9."""
    # URL encode emoji - custom emojis are in format <name:id>
    # Unicode emojis need to be URL encoded
    import urllib.parse
    emoji_encoded = urllib.parse.quote(emoji, safe="")
    
    await discord_api_request(
        "PUT",
        f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji_encoded}/@me",
    )


async def get_user_v9(user_id: str) -> Dict[str, Any]:
    """Get user information using Discord API v9."""
    return await discord_api_request("GET", f"/users/{user_id}")


async def get_guild_members_v9(
    guild_id: str,
    limit: int = 1000,
    after: Optional[str] = None,
) -> list[Dict[str, Any]]:
    """Get guild members using Discord API v9."""
    params = {"limit": min(limit, 1000)}
    if after:
        params["after"] = after
    
    result = await discord_api_request(
        "GET",
        f"/guilds/{guild_id}/members",
        params=params,
    )
    # Ensure we return a list
    if not isinstance(result, list):
        raise ValueError(f"Expected list of members, got {type(result)}: {result}")
    return result