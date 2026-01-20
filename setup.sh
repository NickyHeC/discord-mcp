#!/bin/bash
# Setup script for Discord MCP Server

set -e

echo "Setting up Discord MCP Server..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Get your Discord bot token from https://discord.com/developers/applications"
echo "2. Configure your MCP client (e.g., Claude Desktop) with the DISCORD_TOKEN"
echo "3. See README.md for detailed configuration instructions"
echo ""
