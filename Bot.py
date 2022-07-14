from typing import Optional

import discord
from discord import app_commands
from discord.utils import find

class Bot(discord.client):
    # Constructor for the bot with intents
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
    
    async def on_guild_join(guild):
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