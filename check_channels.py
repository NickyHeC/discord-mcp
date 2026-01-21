#!/usr/bin/env python3
"""
Script to check which channels the bot can access and send messages to.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
from discord_api import (
    get_current_user_guilds_v9,
    get_guild_channels_v9,
)

load_dotenv()


async def main():
    guild_name = "Break In - Dec 2025"
    
    print("=" * 60)
    print("Checking Bot Channel Access")
    print("=" * 60)
    
    # Find the guild
    guilds = await get_current_user_guilds_v9(limit=200)
    guild = None
    for g in guilds:
        if g.get("name") == guild_name:
            guild = g
            break
    
    if not guild:
        print(f"Server '{guild_name}' not found")
        return
    
    guild_id = guild.get("id")
    print(f"\nServer: {guild.get('name')} (ID: {guild_id})")
    
    # Get all channels
    channels = await get_guild_channels_v9(guild_id)
    text_channels = [ch for ch in channels if ch.get("type") == 0]
    
    print(f"\nFound {len(text_channels)} text channels:")
    print("-" * 60)
    
    for channel in sorted(text_channels, key=lambda x: x.get("name", "")):
        name = channel.get("name", "unknown")
        channel_id = channel.get("id")
        print(f"  #{name} (ID: {channel_id})")
    
    print("\n" + "=" * 60)
    print("Note: The bot needs 'Send Messages' permission in a channel")
    print("to be able to post messages there.")


if __name__ == "__main__":
    asyncio.run(main())
