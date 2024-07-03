import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from dotenv import load_dotenv

# Enviromental variables (shoutout to morganite and nomad for the idea!! <3)
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True

# i dont think this is needed but too new to get rid of it :c
bot = commands.Bot(command_prefix="!", intents=intents)

# JSON Black magic wizardy (shout out to demo.py for the idea!! <3)
def load_config():
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    return {"message": "Default message", "log_channel_id": None}

def save_config(config):
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)
config = load_config()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    # Shout out to demo.py again for reccomending removing the sync

@bot.tree.command(name="set-message", description="Set the message to be sent by the updates command.")
# Demo.py again for the reccomendation to use app commands!
@app_commands.checks.has_permissions(administrator=True)
async def set_message(interaction: discord.Interaction, message: str):
    config["message"] = message
    save_config(config)
    await interaction.response.send_message(f"Message set to: {message}")

@bot.tree.command(name="updates", description="Send the set message.")
async def updates(interaction: discord.Interaction):
    await interaction.response.send_message(config["message"])

@bot.tree.command(name="log-channel", description="Set the channel where logs of deleted messages will be sent.")
# Demo.py again for the reccomendation to use app commands!mk
@app_commands.checks.has_permissions(administrator=True)
async def log_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    config["log_channel_id"] = channel.id
    save_config(config)
    await interaction.response.send_message(f"Log channel set to: {channel.mention}")

# Put a end to the stinky ghost pings
@bot.event
async def on_message_delete(message: discord.Message):
    if not message.mentions:
        return

    if config["log_channel_id"]:
        log_channel = bot.get_channel(config["log_channel_id"])
        if log_channel:
            # Construct the log message including the author's username
            log_message = \
                f"Message by {message.author} deleted in {message.channel.mention}:\n" \
                f"Content: {message.content}\n" \
                f"Mentioned Users: {', '.join([user.mention for user in message.mentions])}"
            await log_channel.send(log_message)

# Error handler (shoutout nomad!! <3)
@set_message.error
@log_channel.error
async def on_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
    else:
        await interaction.response.send_message(f"An error occurred: {str(error)}", ephemeral=True)
        raise error  

# Global error handler (shoutout nomad!! <3)
@bot.event
async def on_error(event, *args, **kwargs):
    with open('error.log', 'a') as f:
        if event == 'on_message_delete':
            f.write(f'Unhandled message deletion error: {args[0]}\n')
        else:
            f.write(f'Unhandled error: {args[0]}\n')

if TOKEN:
    bot.run(TOKEN)
else:
    print("Bot token not found. Please set the DISCORD_BOT_TOKEN environment variable.")
