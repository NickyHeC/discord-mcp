# Discord API v9 Usage

This Discord MCP server uses **Discord REST API version 9** exclusively via HTTPS. All operations use HTTPS REST API calls - no WebSocket connections are used.

## Base URL

All API requests are made to:
```
https://discord.com/api/v9
```

## API Versioning

Discord exposes different versions of their API. This server explicitly uses version 9 (v9) by including it in the request path:
- Base URL: `https://discord.com/api/v9`
- Example endpoint: `https://discord.com/api/v9/channels/{channel_id}/messages`

## Authentication

All API requests require authentication using a Bot Token:
```
Authorization: Bot <YOUR_BOT_TOKEN>
```

Set your bot token in the `DISCORD_TOKEN` environment variable (or `.env` file).

## Available API Endpoints

The `src/discord_api.py` module provides helper functions for common Discord API v9 operations:

### Messages
- `send_message_v9(channel_id, content)` - POST `/channels/{channel_id}/messages`
- `get_channel_messages_v9(channel_id, limit, before, after)` - GET `/channels/{channel_id}/messages`
- `delete_message_v9(channel_id, message_id)` - DELETE `/channels/{channel_id}/messages/{message_id}`

### Reactions
- `create_reaction_v9(channel_id, message_id, emoji)` - PUT `/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me`

### Guilds (Servers)
- `get_guild_v9(guild_id)` - GET `/guilds/{guild_id}`
- `get_guild_channels_v9(guild_id)` - GET `/guilds/{guild_id}/channels`
- `get_current_user_guilds_v9(limit)` - GET `/users/@me/guilds`
- `get_guild_members_v9(guild_id, limit, after)` - GET `/guilds/{guild_id}/members`

### Users
- `get_user_v9(user_id)` - GET `/users/{user_id}`

## Direct API Requests

You can also make custom API requests using the `discord_api_request()` function:

```python
from src.discord_api import discord_api_request

# Example: Get a specific channel
channel_data = await discord_api_request(
    "GET",
    f"/channels/{channel_id}"
)

# Example: Update a channel
updated_channel = await discord_api_request(
    "PATCH",
    f"/channels/{channel_id}",
    data={"name": "new-channel-name"}
)
```

## Rate Limiting

Discord API has rate limits. Since this server uses only HTTPS REST API calls, be aware of Discord's rate limits:

- **Global Rate Limit**: 50 requests per second per bot
- **Per-Route Rate Limits**: Vary by endpoint (see Discord API documentation)

## References

- [Discord API Documentation](https://discord.com/developers/docs/reference)
- [Discord API v9 Reference](https://discord.com/developers/docs/reference#api-versioning)
- [Discord API Rate Limits](https://discord.com/developers/docs/topics/rate-limits)
