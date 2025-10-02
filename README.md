# Discord Server Cleanup Bot 🤖

A powerful Discord bot that can instantly delete all channels and categories in a server with a simple `/start` command. Perfect for server customization and cleanup tasks!

## Features ✨

- **Instant Cleanup**: Delete all channels and categories with one command
- **Slash Commands**: Modern Discord slash command interface
- **Safety First**: Administrator permission checks
- **Error Handling**: Comprehensive error reporting
- **Rate Limit Protection**: Built-in delays to avoid Discord API limits
- **Easy Deployment**: Ready for Render deployment

## Commands 📋

- `/start` - Delete all channels and categories in the server
- `/info` - Display bot information and usage instructions

## Setup Instructions 🚀

### 1. Create Discord Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to "Bot" section and click "Add Bot"
4. Copy the bot token (you'll need this later)
5. Enable these bot permissions:
   - `Manage Channels`
   - `Use Slash Commands`

### 2. Invite Bot to Server

1. Go to "OAuth2" > "URL Generator"
2. Select scopes: `bot` and `applications.commands`
3. Select permissions: `Manage Channels`
4. Copy the generated URL and open it to invite the bot

### 3. Local Development

```bash
# Clone or download the project
cd discord-cleanup-bot

# Install dependencies
pip install -r requirements.txt

# Set your bot token as environment variable
# Windows:
set DISCORD_BOT_TOKEN=your_bot_token_here

# Linux/Mac:
export DISCORD_BOT_TOKEN=your_bot_token_here

# Run the bot
python main.py
```

### 4. Deploy to Render

1. Create a new account on [Render](https://render.com)
2. Connect your GitHub repository or upload the files
3. Create a new "Web Service"
4. Use these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Environment Variables**: 
     - `DISCORD_BOT_TOKEN` = your bot token
5. Deploy!

## Usage 💡

1. Make sure you have **Administrator** permissions in the server
2. Type `/start` in any channel
3. Confirm the action (the bot will ask for confirmation)
4. Watch as all channels and categories are deleted instantly!

## Safety Features 🛡️

- **Permission Checks**: Only administrators can use the cleanup command
- **Error Handling**: Graceful handling of permission errors and API limits
- **Rate Limiting**: Built-in delays to prevent Discord API rate limits
- **Detailed Reporting**: Shows exactly what was deleted and any errors

## Important Notes ⚠️

- **This action cannot be undone!** Make sure you really want to delete everything
- The bot needs `Manage Channels` permission to work
- Only users with Administrator permissions can use the `/start` command
- The bot will skip channels it doesn't have permission to delete

## Troubleshooting 🔧

### Bot not responding to slash commands?
- Make sure the bot has been invited with `applications.commands` scope
- Try running `/info` first to test if the bot is working
- Check that the bot is online and has proper permissions

### Getting permission errors?
- Ensure the bot has `Manage Channels` permission
- Make sure your role is higher than the bot's role in the server hierarchy
- Verify you have Administrator permissions

### Rate limit issues?
- The bot includes built-in delays, but for very large servers, it might take longer
- Discord has strict rate limits for channel deletion (about 2 per second)

## Contributing 🤝

Feel free to submit issues, feature requests, or pull requests to improve the bot!

## License 📄

This project is open source and available under the MIT License.
