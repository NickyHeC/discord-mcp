# Discord MCP Server

A Model Context Protocol (MCP) server that enables AI agents to interact with Discord using the Discord REST API v9. This server provides tools for sending messages, reading channel history, managing servers, and more.

## Prerequisites

- Python 3.10 or higher
- A Discord application and bot token
- Basic understanding of Discord bot setup

## Discord Bot Setup

Before using this MCP server, you need to create a Discord application and configure a bot. Please refer to the official Discord Developer documentation:

- **[Overview of Apps](https://discord.com/developers/docs/quick-start/overview-of-apps)** - Learn about Discord applications and bots
- **[Getting Started](https://discord.com/developers/docs/quick-start/getting-started)** - Step-by-step guide to creating your first bot
- **[API Reference](https://discord.com/developers/docs/reference)** - Complete Discord API documentation

### Quick Setup Steps

1. **Create a Discord Application**
   - Go to the [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application" and give it a name
   - Navigate to the **Bot** tab

2. **Create and Configure Your Bot**
   - Click "Add Bot" or "Reset Token" to generate a bot token
   - **Save your bot token securely** - you'll need it for the `.env` file

3. **Enable Privileged Gateway Intents** ⚠️ **IMPORTANT**
   
   In the **Bot** tab, under "Privileged Gateway Intents", you **MUST** enable the following intents:
   
   - ✅ **Presence Intent** - Required for receiving Presence Update events
   - ✅ **Server Members Intent** - Required for receiving GUILD_MEMBERS events
   - ✅ **Message Content Intent** - Required for receiving message content in most messages
   
   **Note:** Once your bot reaches 100 or more servers, these intents will require verification and approval from Discord.

4. **Configure Authorization Flow** (Optional)
   - **Public Bot**: Enable if you want others to be able to add your bot to their servers
   - **Requires OAuth2 Code Grant**: Enable if your application requires multiple scopes

5. **Invite Your Bot to a Server**
   - Go to **OAuth2 > URL Generator**
   - Select the `bot` scope
   - **IMPORTANT**: Select the following permissions:
     - ✅ **View Channels** - Required for `list_channels` tool
     - ✅ **Send Messages** - Required for `send_message` tool
     - ✅ **Read Message History** - Required for `read_messages` tool
     - ✅ **Manage Messages** - Required for `delete_message` tool
     - ✅ **Add Reactions** - Required for `add_reaction` tool
   - Copy the generated URL and invite the bot to your server
   - **Note**: The tool descriptions mention OAuth2 scopes like `guilds.channels.read`, but for bot tokens, these are handled via bot permissions. Ensure the bot has the required permissions listed above.

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd discord-mcp
   ```

2. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```
   
   Or using `uv`:
   ```bash
   uv pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   
   Create a `.env` file in the project root (optional, for local development):
   ```bash
   PORT=8080  # Optional, defaults to 8080
   ```
   
   **Note**: `DISCORD_TOKEN` is passed as a secret from Dedalus via the Connection/SecretValues mechanism. It is accessed in tools via:
   - `ctx.secrets["DISCORD_TOKEN"]`
   
   For local development, you may still use environment variables, but in production/hosted environments, the token should be passed as a secret.

## Running the Server

Start the MCP server:

```bash
python3 -m src.main
```

Or:

```bash
python3 src/main.py
```

The server will start on port 8080 (or the port specified in the `PORT` environment variable).

## Available Tools

The Discord MCP server provides the following tools:

- **`send_message`** - Send a message to a Discord channel. Messages longer than 2000 characters are automatically split into multiple messages.
- **`read_messages`** - Read recent messages from a channel (requires `messages.read` scope). Returns a dict with `count`, `messages` (list of message dicts), and optional `error` field.
- **`list_servers`** - List all Discord servers the bot is in. Returns a list of server dicts with `id`, `name`, `icon`, `owner`, and `permissions`.
- **`get_server_info`** - Get detailed information about a Discord server. Returns a dict with server details including `id`, `name`, `description`, `member_count`, `features`, etc.
- **`list_channels`** - List all channels in a server (requires `guilds.channels.read` scope). Returns a dict with `count`, `channels` (list of channel dicts), and optional `error` field.
- **`add_reaction`** - Add a reaction emoji to a message
- **`delete_message`** - Delete a message from a channel
- **`get_user_info`** - Get information about a Discord user. Returns a dict with user details including `id`, `username`, `discriminator`, `global_name`, `bot`, and `avatar_url`.
- **`list_members`** - List members in a server (requires `guilds.members.read` scope). Returns a dict with `count`, `members` (list of member dicts), and optional `error` field.

### Response Format

All tools return flat JSON-serializable dictionaries (no nested Pydantic models) to ensure compatibility with hosted MCP servers. Read operations that may fail include an optional `error` field in the response for graceful error handling.

## Configuration

### Environment Variables

| Variable | Description | Required | Source |
|----------|-------------|----------|--------|
| `DISCORD_TOKEN` | Your Discord bot token | Yes | Passed as secret from Dedalus via `ctx.secrets["DISCORD_TOKEN"]` |
| `PORT` | Port for the MCP server (default: 8080) | No | Local `.env` file or environment |

**Important**: 
- `DISCORD_TOKEN` is accessed via `ctx.secrets["DISCORD_TOKEN"]` in tools and must be passed as a secret from Dedalus when deploying to a hosted MCP server.
- The Connection definition expects the secret with the exact name: `DISCORD_TOKEN`.

### Channel Permissions

Make sure your bot has the necessary permissions in the channels where you want to use it:

- **View Channels** - Required to see channels
- **Send Messages** - Required to send messages
- **Read Message History** - Required to read messages
- **Manage Messages** - Required to delete messages
- **Add Reactions** - Required to add reactions

## Features

### Automatic Message Chunking

The `send_message` tool automatically handles Discord's 2000 character limit by splitting long messages into multiple messages. This is especially useful when sending long agendas or formatted content.

- Messages are split on line boundaries when possible
- Very long lines are hard-split if necessary
- Each chunk is sent as a separate message
- The tool returns the ID of the last message sent

### Flat JSON Schema

All tools return flat, JSON-serializable dictionaries to ensure compatibility with hosted MCP servers and avoid schema validation issues. This means:

- No nested Pydantic models in responses
- All values are JSON primitives (str, int, bool, list, dict)
- Optional fields are omitted rather than set to null
- Error information is included in an optional `error` field

### Enhanced Error Handling

- Detailed error messages with specific Discord error codes
- Full error response logging for debugging
- Graceful error handling in read operations (errors returned in response, not raised)
- Specific handling for common errors (400, 401, 403, 404, 429)

## Testing

You can test the tools directly using Python:

```python
import asyncio
from src.tools import send_message, read_messages, list_channels

# Test sending a message
asyncio.run(send_message("channel_id", "Hello, Discord!"))

# Test reading messages
asyncio.run(read_messages("channel_id", limit=10))

# Test listing channels
asyncio.run(list_channels("server_id"))
```

## Project Structure

```
discord-mcp/
├── src/
│   ├── main.py          # MCP server entry point
│   ├── tools.py         # Discord tool definitions
│   └── discord_api.py   # Discord API v9 client
├── .env                 # Environment variables (create this)
├── requirements.txt     # Python dependencies
├── pyproject.toml       # Project configuration
└── README.md           # This file
```

## Troubleshooting

### Common Issues

1. **403 Forbidden / Missing Access (especially for `list_channels`)**
   - **For hosted MCP servers**: Ensure the bot token has the required permissions when it was invited to the server
   - Check that the bot's role has "View Channels" permission in the server
   - Go to Server Settings > Roles > [Your Bot's Role] and verify "View Channels" is enabled
   - If the bot was invited without proper permissions, re-invite it with all required permissions (see step 5 in Discord Bot Setup)
   - **For hosted servers on dedaluslabs.ai**: Verify that `DISCORD_TOKEN` is correctly configured in the server's environment variables
   - The error response will include detailed information about what permission is missing

2. **401 Unauthorized**
   - Verify the `DISCORD_TOKEN` is correct and not expired
   - Check that there are no extra spaces or quotes around the token in your `.env` file
   - For hosted MCP servers, ensure the token is properly passed via the Connection/SecretValues mechanism
   - Regenerate the token in the Discord Developer Portal if needed

3. **Message too long (400 / Invalid Form Body)**
   - Discord has a 2000 character limit per message
   - The `send_message` tool automatically splits messages longer than 2000 characters into multiple messages
   - If you still see this error, check the error message for details about what went wrong
   - Error responses now include full validation details for easier debugging

4. **Read tools return error field in hosted MCP server**
   - All read tools (`list_channels`, `read_messages`, `list_members`, etc.) may return an `error` field in the response
   - This usually indicates a permission issue (403) or authentication issue (401)
   - Check the `error` field in the response dict for specific details
   - Verify the bot has the required permissions in the target server
   - Ensure the bot token is valid and properly configured in the hosted environment
   - Agents should check the `error` field in responses and handle errors gracefully

5. **SSL Certificate Errors**
   - The code uses `certifi` for SSL certificate verification
   - If you encounter SSL errors, ensure `certifi` is installed: `pip3 install certifi`

6. **Intents Not Working**
   - Make sure you've enabled the required Privileged Gateway Intents in the Discord Developer Portal
   - Restart the bot after enabling intents

7. **Rate Limiting (429)**
   - Discord may rate limit requests if you send too many messages too quickly
   - The error message will include retry timing information
   - Implement backoff logic in your agent when handling 429 errors

### Hosted MCP Server Issues

When using this MCP server on a hosted platform (e.g., dedaluslabs.ai):

1. **Credentials Configuration**
   - `DISCORD_TOKEN` must be passed as a secret from Dedalus via the Connection/SecretValues mechanism
   - The token is accessed in tools via:
     - `ctx.secrets["DISCORD_TOKEN"]`
   - Verify the token is not expired or invalid

2. **Permission Errors**
   - Hosted servers use the same bot token, so permissions must be granted when the bot is invited
   - If `list_channels` fails with 403, the bot needs "View Channels" permission in the server
   - Re-invite the bot with proper permissions if needed

3. **Error Visibility**
   - All read tools return errors in the `error` field of their response dicts
   - Agents should check `response.get("error")` to see detailed error messages
   - Error messages include specific guidance on how to fix permission issues
   - Full error responses are logged for debugging (check server logs for details)

4. **Message Chunking**
   - Long messages (>2000 chars) are automatically split into multiple messages
   - Each chunk is sent as a separate message
   - The tool returns the ID of the last message sent
   - This prevents 400 errors from message length violations

## API Documentation

This server uses Discord REST API version 9. For detailed API documentation, refer to:

- **[Discord API Reference](https://discord.com/developers/docs/reference)** - Complete API reference
- **[Discord API v9 Documentation](API_V9.md)** - API v9 specific documentation
- **[Authentication Guide](AUTHENTICATION.md)** - Authentication setup guide

## License

MIT License - see [LICENSE](LICENSE) file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues related to:
- **Discord API**: Refer to [Discord Developer Documentation](https://discord.com/developers/docs)
- **This Project**: Open an issue on the repository

---

**Important Reminder:** Don't forget to enable the **Privileged Gateway Intents** (Presence Intent, Server Members Intent, and Message Content Intent) in your Discord bot settings, as shown in the Discord Developer Portal!
