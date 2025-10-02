import discord
from discord.ext import commands
import asyncio
import os
from typing import List

# Bot setup with minimal intents (no privileged intents required)
intents = discord.Intents.default()
intents.guilds = True
# Remove message_content intent as it's privileged and not needed for slash commands

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="start", description="Delete all channels and categories in the server")
async def start_cleanup(interaction: discord.Interaction):
    """
    Slash command to delete all channels and categories in the server
    """
    # Check if user has administrator permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need Administrator permissions to use this command!", ephemeral=True)
        return
    
    # Defer the response since this might take a while
    await interaction.response.defer()
    
    guild = interaction.guild
    deleted_channels = 0
    deleted_categories = 0
    errors = []
    
    try:
        # Send initial status message
        await interaction.followup.send("🚀 Starting server cleanup... This may take a few moments.")
        
        # Get all channels and categories
        channels_to_delete = []
        categories_to_delete = []
        
        for channel in guild.channels:
            if isinstance(channel, discord.CategoryChannel):
                categories_to_delete.append(channel)
                print(f"Found category: {channel.name}")
            else:
                channels_to_delete.append(channel)
                print(f"Found channel: {channel.name} (type: {type(channel).__name__})")
        
        print(f"Total found: {len(channels_to_delete)} channels, {len(categories_to_delete)} categories")
        
        # Delete all regular channels first
        for channel in channels_to_delete:
            try:
                await channel.delete(reason="Server cleanup requested by administrator")
                deleted_channels += 1
                print(f"Deleted channel: {channel.name}")
                # Small delay to avoid rate limits
                await asyncio.sleep(0.5)
            except discord.Forbidden:
                errors.append(f"No permission to delete channel: {channel.name}")
            except discord.NotFound:
                # Channel already deleted
                pass
            except Exception as e:
                errors.append(f"Error deleting channel {channel.name}: {str(e)}")
        
        # Send update message before deleting categories
        if categories_to_delete:
            await interaction.followup.send(f"🗂️ Now deleting {len(categories_to_delete)} categories...")
        
        # Delete all categories after channels
        for category in categories_to_delete:
            try:
                await category.delete(reason="Server cleanup requested by administrator")
                deleted_categories += 1
                print(f"Deleted category: {category.name}")
                # Small delay to avoid rate limits
                await asyncio.sleep(0.5)
            except discord.Forbidden:
                errors.append(f"No permission to delete category: {category.name}")
                print(f"Permission denied for category: {category.name}")
            except discord.NotFound:
                # Category already deleted
                print(f"Category not found (already deleted): {category.name}")
                pass
            except Exception as e:
                errors.append(f"Error deleting category {category.name}: {str(e)}")
                print(f"Error deleting category {category.name}: {str(e)}")
        
        # Send completion message
        success_msg = f"✅ **Cleanup Complete!**\n"
        success_msg += f"🗑️ Deleted {deleted_channels} channels\n"
        success_msg += f"📁 Deleted {deleted_categories} categories\n"
        
        if errors:
            success_msg += f"\n⚠️ **Errors encountered:**\n"
            for error in errors[:5]:  # Show only first 5 errors to avoid message length issues
                success_msg += f"• {error}\n"
            if len(errors) > 5:
                success_msg += f"• ... and {len(errors) - 5} more errors\n"
        
        await interaction.followup.send(success_msg)
        
    except Exception as e:
        await interaction.followup.send(f"❌ An unexpected error occurred: {str(e)}")
        print(f"Unexpected error in start_cleanup: {e}")

@bot.tree.command(name="info", description="Get information about the bot")
async def bot_info(interaction: discord.Interaction):
    """
    Display bot information and usage instructions
    """
    embed = discord.Embed(
        title="🤖 Discord Server Cleanup Bot",
        description="A bot designed to quickly clean up Discord servers by deleting all channels and categories.",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="📋 Commands",
        value="`/start` - Delete all channels and categories\n`/info` - Show this information",
        inline=False
    )
    
    embed.add_field(
        name="⚠️ Requirements",
        value="• You must have Administrator permissions\n• Bot must have Manage Channels permission",
        inline=False
    )
    
    embed.add_field(
        name="🛡️ Safety Features",
        value="• Permission checks before execution\n• Error handling and reporting\n• Rate limit protection",
        inline=False
    )
    
    embed.set_footer(text="Use with caution - this action cannot be undone!")
    
    await interaction.response.send_message(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore unknown commands
    
    print(f"Command error: {error}")
    await ctx.send(f"An error occurred: {str(error)}")

# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("❌ Error: DISCORD_BOT_TOKEN environment variable not found!")
        print("Please set your Discord bot token as an environment variable.")
        exit(1)
    
    bot.run(token)
