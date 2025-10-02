import discord
from discord.ext import commands
import asyncio
import os
from typing import List
from flask import Flask, jsonify
import threading

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
        try:
            await interaction.response.send_message("❌ You need Administrator permissions to use this command!", ephemeral=True)
        except discord.errors.NotFound:
            print("Interaction expired - user lacks admin permissions")
        return
    
    # Immediately respond to avoid timeout
    try:
        await interaction.response.send_message("🚀 Starting server cleanup... This will take a few moments!", ephemeral=True)
    except discord.errors.NotFound:
        print("Interaction expired - cannot respond, but continuing with cleanup")
        # Continue anyway, just log to console
    
    guild = interaction.guild
    deleted_channels = 0
    deleted_categories = 0
    errors = []
    
    try:
        # Send initial status message (if interaction is still valid)
        try:
            await interaction.followup.send("🚀 Starting server cleanup... This may take a few moments.")
        except (discord.errors.HTTPException, discord.errors.NotFound):
            print("🚀 Starting server cleanup... This may take a few moments.")
        
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
        for i, channel in enumerate(channels_to_delete):
            try:
                await channel.delete(reason="Server cleanup requested by administrator")
                deleted_channels += 1
                print(f"Deleted channel: {channel.name}")
                
                # Send progress update every 10 deletions to keep interaction alive
                if (i + 1) % 10 == 0:
                    try:
                        await interaction.followup.send(f"🗑️ Progress: Deleted {deleted_channels} channels so far...")
                    except discord.errors.HTTPException:
                        # Interaction expired, just log to console
                        print(f"Progress: Deleted {deleted_channels} channels so far...")
                
                # Smaller delay to avoid timeouts but still respect rate limits
                await asyncio.sleep(0.2)
            except discord.Forbidden:
                errors.append(f"No permission to delete channel: {channel.name}")
            except discord.NotFound:
                # Channel already deleted
                pass
            except Exception as e:
                errors.append(f"Error deleting channel {channel.name}: {str(e)}")
        
        # Send update message before deleting categories
        if categories_to_delete:
            try:
                await interaction.followup.send(f"🗂️ Now deleting {len(categories_to_delete)} categories...")
            except discord.errors.HTTPException:
                # Interaction expired, just log to console
                print(f"Now deleting {len(categories_to_delete)} categories...")
        
        # Delete all categories after channels
        for category in categories_to_delete:
            try:
                await category.delete(reason="Server cleanup requested by administrator")
                deleted_categories += 1
                print(f"Deleted category: {category.name}")
                # Smaller delay to avoid timeouts but still respect rate limits
                await asyncio.sleep(0.2)
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
        
        try:
            await interaction.followup.send(success_msg)
        except discord.errors.HTTPException:
            # Interaction expired, just log to console
            print("Cleanup complete! Check Discord for results.")
            print(f"Deleted {deleted_channels} channels and {deleted_categories} categories")
        
    except Exception as e:
        try:
            await interaction.followup.send(f"❌ An unexpected error occurred: {str(e)}")
        except discord.errors.HTTPException:
            # Interaction expired, just log to console
            print(f"Unexpected error in start_cleanup: {e}")
        print(f"Unexpected error in start_cleanup: {e}")

@bot.tree.command(name="test", description="Create 50 test channels for testing the cleanup bot")
async def create_test_channels(interaction: discord.Interaction):
    """
    Create 50 test channels and some categories for testing purposes
    """
    # Check if user has administrator permissions
    if not interaction.user.guild_permissions.administrator:
        try:
            await interaction.response.send_message("❌ You need Administrator permissions to use this command!", ephemeral=True)
        except discord.errors.NotFound:
            print("Interaction expired - user lacks admin permissions")
        return
    
    # Immediately respond to avoid timeout
    try:
        await interaction.response.send_message("🧪 Starting test channel creation... This will take about 10-15 seconds!", ephemeral=True)
    except discord.errors.NotFound:
        print("Interaction expired - cannot respond, but continuing with channel creation")
        # Continue anyway, just log to console
    
    guild = interaction.guild
    created_channels = 0
    created_categories = 0
    errors = []
    
    try:
        # Send initial status message (if interaction is still valid)
        try:
            await interaction.followup.send("🧪 Creating test channels and categories... This may take a few moments.")
        except (discord.errors.HTTPException, discord.errors.NotFound):
            print("🧪 Creating test channels and categories... This may take a few moments.")
        
        # Create 5 test categories first
        categories = []
        category_names = ["Test Category 1", "Test Category 2", "Test Category 3", "Test Category 4", "Test Category 5"]
        
        for cat_name in category_names:
            try:
                category = await guild.create_category(cat_name, reason="Test channels for cleanup bot testing")
                categories.append(category)
                created_categories += 1
                print(f"Created category: {cat_name}")
                await asyncio.sleep(0.2)  # Rate limit protection
            except Exception as e:
                errors.append(f"Error creating category {cat_name}: {str(e)}")
        
        # Create 50 test channels (10 in each category)
        channel_count = 0
        for i in range(50):
            try:
                # Distribute channels across categories
                category = categories[i % len(categories)] if categories else None
                channel_name = f"test-channel-{i+1:02d}"
                
                await guild.create_text_channel(
                    channel_name, 
                    category=category,
                    reason="Test channel for cleanup bot testing"
                )
                created_channels += 1
                channel_count += 1
                print(f"Created channel: {channel_name}")
                
                # Send progress update every 10 channels (with error handling)
                if channel_count % 10 == 0:
                    try:
                        await interaction.followup.send(f"🔄 Progress: Created {created_channels} channels so far...")
                    except discord.errors.HTTPException:
                        # Interaction expired, just log to console
                        print(f"Progress: Created {created_channels} channels so far...")
                
                await asyncio.sleep(0.2)  # Rate limit protection
                
            except Exception as e:
                errors.append(f"Error creating channel test-channel-{i+1:02d}: {str(e)}")
        
        # Send completion message
        success_msg = f"✅ **Test Setup Complete!**\n"
        success_msg += f"📁 Created {created_categories} categories\n"
        success_msg += f"💬 Created {created_channels} channels\n\n"
        success_msg += f"🎯 **Ready for testing!** Use `/start` to delete everything instantly!"
        
        if errors:
            success_msg += f"\n⚠️ **Errors encountered:**\n"
            for error in errors[:3]:  # Show only first 3 errors
                success_msg += f"• {error}\n"
            if len(errors) > 3:
                success_msg += f"• ... and {len(errors) - 3} more errors\n"
        
        try:
            await interaction.followup.send(success_msg)
        except discord.errors.HTTPException:
            # Interaction expired, just log to console
            print("Test setup complete! Check Discord for results.")
            print(f"Created {created_categories} categories and {created_channels} channels")
        
    except Exception as e:
        try:
            await interaction.followup.send(f"❌ An unexpected error occurred: {str(e)}")
        except discord.errors.HTTPException:
            # Interaction expired, just log to console
            print(f"Unexpected error in create_test_channels: {e}")
        print(f"Unexpected error in create_test_channels: {e}")

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
        value="`/start` - Delete all channels and categories\n`/test` - Create 50 test channels for testing\n`/info` - Show this information",
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

# Flask web server for Render
app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "bot": "Discord Cleanup Bot",
        "message": "Bot is running! Use /start command in Discord to delete all channels and categories."
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "bot_connected": bot.is_ready()})

@app.route('/stats')
def stats():
    if bot.is_ready():
        return jsonify({
            "status": "connected",
            "guilds": len(bot.guilds),
            "latency": round(bot.latency * 1000, 2)
        })
    else:
        return jsonify({"status": "disconnected"})

def run_bot():
    """Run the Discord bot in a separate thread"""
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("❌ Error: DISCORD_BOT_TOKEN environment variable not found!")
        return
    
    try:
        bot.run(token)
    except Exception as e:
        print(f"Bot error: {e}")

def run_flask():
    """Run the Flask web server"""
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

# Run both bot and web server
if __name__ == "__main__":
    # Start Discord bot in background thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    print("🚀 Starting Discord bot and web server...")
    print("🤖 Bot will be available for /start command")
    print(f"🌐 Web server will be available on port {os.getenv('PORT', 10000)}")
    
    # Start Flask web server (main thread)
    run_flask()
