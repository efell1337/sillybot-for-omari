import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import CommandSyncFailure

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.guild_reactions = True

# i dont think this is needed but too new to get rid of it :c
bot = commands.Bot(command_prefix="!", intents=intents)

# you can either hard code the message and channel or set it via the commands
config = {
    "message": "Default message",
    "log_channel_id": None
}

def is_admin(interaction: discord.Interaction):
    return interaction.user.guild_permissions.administrator

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.tree.sync()

@bot.tree.command(name="set-message", description="Set the message to be sent by the updates command.")
async def set_message(interaction: discord.Interaction, message: str):
    if not is_admin(interaction):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    config["message"] = message
    await interaction.response.send_message(f"Message set to: {message}")

@bot.tree.command(name="updates", description="Send the set message.")
async def updates(interaction: discord.Interaction):
    await interaction.response.send_message(config["message"])

@bot.tree.command(name="log-channel", description="Set the channel where logs of deleted messages will be sent.")
async def log_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    if not is_admin(interaction):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    config["log_channel_id"] = channel.id
    await interaction.response.send_message(f"Log channel set to: {channel.mention}")

@bot.event
async def on_message_delete(message: discord.Message):
    if not message.mentions:
        return

    if config["log_channel_id"]:
        log_channel = bot.get_channel(config["log_channel_id"])
        if log_channel:
            log_message = (
                f"Ghost Ping by : __{message.author.name}__ Deleted in : {message.channel.mention}:\n"
                f"Content: {message.content}\n"
                f"Mentioned Users: {', '.join([user.mention for user in message.mentions])}"
            )
            await log_channel.send(log_message)

# Insert bot token here pls :3
bot.run('REPLACE_ME')
