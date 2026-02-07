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
from dedalus_mcp import get_context

# Load environment variables from .env file
load_dotenv()

# Discord API Configuration
DISCORD_API_BASE_URL = "https://discord.com/api/v9"
# DISCORD_TOKEN is accessed via ctx.secrets


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
        token: Discord bot token (defaults to ctx.secrets["token"])
        data: Request body data (will be JSON encoded)
        params: URL query parameters
    
    Returns:
        JSON response as dictionary
    
    Raises:
        ValueError: If token is missing
        aiohttp.ClientResponseError: For HTTP errors
    """
    # Get token from context secrets if not provided
    if not token:
        try:
            ctx = get_context()
            token = ctx.secrets["token"]
        except (LookupError, KeyError) as e:
            raise ValueError("Discord token not found. Ensure the token is passed as a secret from Dedalus (ctx.secrets['token']).") from e
    
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
                # Try to parse JSON error for better error messages
                error_code = ""
                error_message = error_text
                error_details = {}
                try:
                    import json
                    error_json = json.loads(error_text)
                    error_code = error_json.get("code", "")
                    error_message = error_json.get("message", error_text)
                    # Include full error details for debugging (especially useful for 400 errors)
                    error_details = error_json
                except (ValueError, json.JSONDecodeError):
                    # Not JSON, use raw text
                    pass
                
                # Log the full error response for debugging (especially important for 400 errors)
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Discord API error [{response.status}]: {error_text}")
                
                # Provide helpful context for common errors
                if response.status == 400:
                    # 400 errors often include detailed validation info in the response
                    if error_code == 50035:  # Invalid Form Body
                        # Include validation errors if present
                        if "errors" in error_details:
                            validation_errors = error_details.get("errors", {})
                            error_message = f"Invalid Form Body (400): {error_message}. Validation errors: {validation_errors}"
                        else:
                            error_message = f"Invalid Form Body (400): {error_message}. Check request format and content length (max 2000 chars for messages)."
                    else:
                        error_message = f"Bad Request (400): {error_message}. Full error: {error_text}"
                elif response.status == 403:
                    if error_code == 50001:  # Missing Access
                        error_message = f"Missing Access (403): {error_message}. The bot may lack required permissions. For list_channels, ensure the bot has 'View Channels' permission in the server."
                    elif error_code == 50013:  # Missing Permissions
                        error_message = f"Missing Permissions (403): {error_message}. Check bot permissions in server settings. The bot needs 'View Channels' permission to list channels."
                    else:
                        error_message = f"Permission denied (403): {error_message}. The bot may lack required permissions. Check server role permissions."
                elif response.status == 401:
                    error_message = f"Unauthorized (401): {error_message}. Check that the Discord token (ctx.secrets['DISCORD_TOKEN']) is valid, not expired, and properly configured in the hosted MCP server environment."
                elif response.status == 404:
                    error_message = f"Not Found (404): {error_message}. The resource may not exist or the bot may not have access."
                elif response.status == 429:
                    retry_after = error_details.get("retry_after") if error_details else None
                    if retry_after:
                        error_message = f"Rate Limited (429): {error_message}. Retry after {retry_after} seconds."
                    else:
                        error_message = f"Rate Limited (429): {error_message}. Please retry with backoff."
                
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message=f"Discord API error [{error_code}]: {error_message}" if error_code else f"Discord API error: {error_message}"
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