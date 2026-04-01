# Authentication Verification

## Bot Token Authentication

This Discord MCP server uses **Bot Token** authentication as specified in the Discord API documentation.

### Authentication Header Format

According to Discord API documentation, bot requests use:

- **Bot token**: `Authorization: Bot <your-bot-token>`
- **OAuth2 user token**: `Authorization: Bearer <token>`

This server uses the **bot token** style. In `dedalus_mcp`, the `Connection` header template must include the literal placeholder **`{api_key}`** (the framework substitutes your secret with `.format(api_key=...)`). Use:

```text
auth_header_format="Bot {api_key}"
```

in `src/main.py` — the value is still your Discord bot token; only the template placeholder name is fixed by the SDK.

### Implementation

**Location**: `src/main.py` (`Connection`) and `src/discord_api.py` (`ctx.dispatch` to Discord REST v9).

### Environment Variables

**Local `.env`:** copy `.env.example` to `.env`. At minimum set `DISCORD_TOKEN` for local runs and `python -m src.client --test-connection`.

**Loading mechanism:**
- `python-dotenv` loads `.env` in `src/main.py` and `src/client.py`
- Hosted: DAuth supplies the bot token; tools use `ctx.dispatch("discord", ...)` — no raw token in server code

### Verification Checklist

✅ **Connection**: `auth_header_format="Bot {api_key}"` with `SecretKeys(token="DISCORD_TOKEN")`  
✅ **Local token**: `DISCORD_TOKEN` in `.env` for `ConnectionTester` and local dispatch  
✅ **Error handling**: Failed requests surface errors in tool responses or logs as documented in the README  

### Security Notes

- The `.env` file is excluded from version control (in `.gitignore`)
- Never commit bot tokens to the repository
- Bot tokens should be kept secure and rotated if compromised
