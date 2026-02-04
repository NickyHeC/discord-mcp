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
   
   Create a `.env` file in the project root:
   ```bash
   DISCORD_TOKEN=your_bot_token_here
   APP_ID=your_application_id_here
   PUBLIC_KEY=your_public_key_here
   PORT=8080  # Optional, defaults to 8080
   ```
   
   Replace the placeholder values with your actual Discord application credentials.

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

- **`send_message`** - Send a message to a Discord channel
- **`read_messages`** - Read recent messages from a channel (requires `messages.read` scope)
- **`list_servers`** - List all Discord servers the bot is in
- **`get_server_info`** - Get detailed information about a Discord server
- **`list_channels`** - List all channels in a server (requires `guilds.channels.read` scope)
- **`add_reaction`** - Add a reaction emoji to a message
- **`delete_message`** - Delete a message from a channel
- **`get_user_info`** - Get information about a Discord user
- **`list_members`** - List members in a server (requires `guilds.members.read` scope)

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DISCORD_TOKEN` | Your Discord bot token | Yes |
| `APP_ID` | Your Discord application ID | Optional |
| `PUBLIC_KEY` | Your Discord application public key | Optional |
| `PORT` | Port for the MCP server (default: 8080) | No |

### Channel Permissions

Make sure your bot has the necessary permissions in the channels where you want to use it:

- **View Channels** - Required to see channels
- **Send Messages** - Required to send messages
- **Read Message History** - Required to read messages
- **Manage Messages** - Required to delete messages
- **Add Reactions** - Required to add reactions

## Testing

### Test Scripts

The repository includes test scripts to verify the setup:

1. **Test reading messages:**
   ```bash
   python3 test_break_in_server.py
   ```
   This script retrieves the most recent message from the #announcements channel.

2. **Test sending messages:**
   ```bash
   python3 send_test_message.py
   ```
   This script sends a test message to a Discord channel.

3. **Check channel access:**
   ```bash
   python3 check_channels.py
   ```
   This script lists all channels the bot can access.

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

3. **`list_channels` returns error field in hosted MCP server**
   - This usually indicates a permission issue (403) or authentication issue (401)
   - Check the `error` field in the `ChannelsResponse` for specific details
   - Verify the bot has "View Channels" permission in the target server
   - Ensure the bot token is valid and properly configured in the hosted environment
   - The agent should check the `error` field in the response and handle it gracefully

4. **SSL Certificate Errors**
   - The code uses `certifi` for SSL certificate verification
   - If you encounter SSL errors, ensure `certifi` is installed: `pip3 install certifi`

5. **Intents Not Working**
   - Make sure you've enabled the required Privileged Gateway Intents in the Discord Developer Portal
   - Restart the bot after enabling intents

### Hosted MCP Server Issues

When using this MCP server on a hosted platform (e.g., dedaluslabs.ai):

1. **Credentials Configuration**
   - Ensure `DISCORD_TOKEN`, `APP_ID`, and `PUBLIC_KEY` are set in the hosted environment
   - The credentials should be passed via the Connection/SecretValues mechanism if using Dedalus Labs
   - Verify credentials are not expired or invalid

2. **Permission Errors**
   - Hosted servers use the same bot token, so permissions must be granted when the bot is invited
   - If `list_channels` fails with 403, the bot needs "View Channels" permission in the server
   - Re-invite the bot with proper permissions if needed

3. **Error Visibility**
   - The `list_channels` tool now returns errors in the `error` field of `ChannelsResponse`
   - Agents should check `response.error` to see detailed error messages
   - Error messages include specific guidance on how to fix permission issues

## API Documentation

This server uses Discord REST API version 9. For detailed API documentation, refer to:

- **[Discord API Reference](https://discord.com/developers/docs/reference)** - Complete API reference
- **[Discord API v9 Documentation](API_V9.md)** - API v9 specific documentation
- **[Authentication Guide](AUTHENTICATION.md)** - Authentication setup guide
- **[API Compliance](API_COMPLIANCE.md)** - Compliance with Discord API standards

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
