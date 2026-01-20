# Discord MCP Server

A Model Context Protocol (MCP) server that enables AI agents to interact with Discord. This server provides tools for sending messages, reading channel history, managing servers, and more.

## Features

- **Send Messages**: Send messages to any Discord channel
- **Read Messages**: Retrieve recent messages from channels
- **Server Management**: List servers, get server info, and list members
- **Channel Management**: List channels in servers
- **Message Actions**: Add reactions and delete messages
- **User Information**: Get user details

## Prerequisites

1. **Python 3.10+** installed on your system
2. **Discord Bot Token** - You'll need to create a Discord application and bot

### Setting Up a Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Navigate to the **Bot** tab
4. Click "Reset Token" to generate a bot token (save this securely!)
5. Under **Privileged Gateway Intents**, enable:
   - ✅ PRESENCE INTENT
   - ✅ SERVER MEMBERS INTENT
   - ✅ MESSAGE CONTENT INTENT
6. Go to **OAuth2 > URL Generator**
   - Select the `bot` scope
   - Select permissions: `Send Messages`, `Read Message History`, `View Channels`, `Manage Messages`
   - Copy the generated URL and invite the bot to your server

## Installation

1. Clone or download this repository:
   ```bash
   git clone <repository-url>
   cd discord-mcp
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### For Claude Desktop

1. Locate your Claude Desktop configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add the Discord MCP server configuration:
   ```json
   {
     "mcpServers": {
       "discord": {
         "command": "python",
         "args": ["/path/to/discord-mcp/server.py"],
         "env": {
           "DISCORD_TOKEN": "your_bot_token_here"
         }
       }
     }
   }
   ```

   **Note**: Replace `/path/to/discord-mcp/server.py` with the absolute path to the `server.py` file in this repository.

### For Other MCP Clients

The server communicates via stdio (standard input/output). Configure your MCP client to run:
```bash
python /path/to/discord-mcp/server.py
```

Make sure the `DISCORD_TOKEN` environment variable is set with your bot token.

## Usage

Once configured, the MCP server exposes the following tools:

### Available Tools

#### `send_message`
Send a message to a Discord channel.

**Parameters:**
- `channel_id` (string, required): The Discord channel ID
- `content` (string, required): The message content to send

#### `read_messages`
Read recent messages from a Discord channel.

**Parameters:**
- `channel_id` (string, required): The Discord channel ID
- `limit` (integer, optional): Maximum number of messages (default: 50, max: 100)

#### `list_servers`
List all Discord servers (guilds) the bot is in.

**Parameters:** None

#### `get_server_info`
Get detailed information about a Discord server.

**Parameters:**
- `server_id` (string, required): The Discord server (guild) ID

#### `list_channels`
List all channels in a Discord server.

**Parameters:**
- `server_id` (string, required): The Discord server (guild) ID

#### `add_reaction`
Add a reaction emoji to a message.

**Parameters:**
- `channel_id` (string, required): The Discord channel ID
- `message_id` (string, required): The Discord message ID
- `emoji` (string, required): The emoji to add (e.g., '👍', '❤️', or custom emoji name)

#### `delete_message`
Delete a message from a Discord channel.

**Parameters:**
- `channel_id` (string, required): The Discord channel ID
- `message_id` (string, required): The Discord message ID

#### `get_user_info`
Get information about a Discord user.

**Parameters:**
- `user_id` (string, required): The Discord user ID

#### `list_members`
List members in a Discord server.

**Parameters:**
- `server_id` (string, required): The Discord server (guild) ID
- `limit` (integer, optional): Maximum number of members (default: 100, max: 1000)

## Getting Channel and Server IDs

To use the tools, you'll need Discord IDs. Here's how to get them:

1. **Enable Developer Mode** in Discord:
   - Go to User Settings → Advanced
   - Enable "Developer Mode"

2. **Get Channel ID**: Right-click on a channel → "Copy ID"
3. **Get Server ID**: Right-click on the server name → "Copy ID"
4. **Get User ID**: Right-click on a user → "Copy ID"
5. **Get Message ID**: Right-click on a message → "Copy ID"

## Troubleshooting

### Bot Not Connecting
- Verify your `DISCORD_TOKEN` is correct
- Ensure all required intents are enabled in the Discord Developer Portal
- Check that the bot has been invited to at least one server

### Channel/Server Not Found
- Verify the IDs are correct (they should be numeric strings)
- Ensure the bot has access to the channel/server
- Check that the bot has the necessary permissions

### Permission Errors
- Make sure the bot has the required permissions in the server
- Verify the bot's role has appropriate permissions in the channel

## Development

To run the server directly for testing:

```bash
export DISCORD_TOKEN="your_bot_token_here"
python server.py
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
