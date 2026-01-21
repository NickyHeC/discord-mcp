# Authentication Verification

## Bot Token Authentication

This Discord MCP server uses **Bot Token** authentication as specified in the Discord API documentation.

### Authentication Header Format

According to Discord API documentation:
- **Bot Token**: `Authorization: Bot {token}`
- **OAuth2 Bearer Token**: `Authorization: Bearer {token}`

This server uses the **Bot Token** format, which is correct for bot applications.

### Implementation

**Location**: `src/discord_api.py`

```python
headers = {
    "Authorization": f"Bot {token}",
    "Content-Type": "application/json",
    "User-Agent": "DiscordBot (discord-mcp, 0.1.0)",
}
```

✅ **Correct Format**: `Authorization: Bot {token}`

### Environment Variables

The bot token is loaded from the `.env` file:

**`.env` file structure:**
```
DISCORD_TOKEN=<YOUR_BOT_TOKEN>
APP_ID=<YOUR_APP_ID>
PUBLIC_KEY=<YOUR_PUBLIC_KEY>
```

**Loading mechanism:**
- Uses `python-dotenv` to load `.env` file
- `load_dotenv()` is called in both `discord_api.py` and `main.py`
- Token is read via `os.getenv("DISCORD_TOKEN")`

### Verification Checklist

✅ **Authorization header format**: Correct (`Bot {token}`)  
✅ **Environment variable loading**: `.env` file is loaded using `python-dotenv`  
✅ **Token validation**: Code checks if token exists before making requests  
✅ **Error handling**: Raises `ValueError` if token is missing  

### Security Notes

- The `.env` file is excluded from version control (in `.gitignore`)
- Never commit bot tokens to the repository
- Bot tokens should be kept secure and rotated if compromised
