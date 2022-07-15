import discord
from discord import app_commands
from discord.ext import commands

class pingCog(commands.Cog):
    # Constructor for the bot.
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # /ping command
    @app_commands.command(name="ping", description="pong")
    async def ping(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("pong", ephemeral=True)