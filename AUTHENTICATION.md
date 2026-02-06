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

**Local `.env` file structure:**
```
DISCORD_APP_ID=<YOUR_APPLICATION_ID>
DISCORD_PUBLIC_KEY=<YOUR_PUBLIC_KEY>
PORT=8080  # Optional
```

**Loading mechanism:**
- Uses `python-dotenv` to load `.env` file
- `load_dotenv()` is called in both `discord_api.py` and `main.py`
- `DISCORD_APP_ID` and `DISCORD_PUBLIC_KEY` are read from `.env` file and validated at startup
- `DISCORD_TOKEN` is passed as a secret from Dedalus and accessed via `ctx.secrets["token"]` in tools
- Token is retrieved using `get_context()` from `dedalus_mcp` and accessed as `ctx.secrets["token"]`

### Verification Checklist

✅ **Authorization header format**: Correct (`Bot {token}`)  
✅ **Environment variable loading**: `.env` file is loaded using `python-dotenv`  
✅ **Token validation**: Code checks if token exists before making requests  
✅ **Error handling**: Raises `ValueError` if token is missing  

### Security Notes

- The `.env` file is excluded from version control (in `.gitignore`)
- Never commit bot tokens to the repository
- Bot tokens should be kept secure and rotated if compromised
