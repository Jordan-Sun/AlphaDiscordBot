import logging
import crests

import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import find

class slashCommandCog(commands.Cog):
    # Constructor for the bot.
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        # Send a message to the general channel if it exists and the bot could send messages.
        general = find(lambda x: x.name == 'general',  guild.text_channels)
        if general and general.permissions_for(guild.me).send_messages:
            await general.send('Enhancing {} with my magic power!'.format(guild.name))
        # Copy the global commands over to the newly joined guild.
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        # Send a message when the command tree is synced.
        general = find(lambda x: x.name == 'general',  guild.text_channels)
        if general and general.permissions_for(guild.me).send_messages:
            await general.send('Enhanced {} with my magic power!'.format(guild.name))

    @app_commands.command(name="ping", description="pong")
    async def ping(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("pong", ephemeral=True)

    @app_commands.command(name="rift", description="run some rifts")
    async def rift(self, interaction: discord.Interaction, runs: int = 1) -> None:
        await interaction.response.send_message(crests.gems(runs), ephemeral=True)