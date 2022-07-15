import logging

import discord
from discord.ext import commands
from discord.utils import find

import cogs

class AlphaBot(commands.Bot):
    def __init__(self, command_prefix='!', description='', intents=discord.Intents.all()):
        super().__init__(command_prefix=command_prefix, description=description, intents=intents)
    
    async def on_ready(self):
        # Log the bot in.
        logging.info('Logged in as {0}.'.format(self.user))
        await self.change_presence(activity=discord.Game(name='Discord'))
        # Register the commands to all guilds.
        for guild in self.guilds:
            await self.sync_commands(guild=guild)
    
    async def on_guild_join(self, guild):
        await self.sync_commands(guild=guild)

    async def sync_commands(self, guild):
        # Send a message to the general channel if it exists and the bot could send messages.
        general = find(lambda x: x.name == 'general',  guild.text_channels)
        if general and general.permissions_for(guild.me).send_messages:
            await general.send('Enhancing {} with my magic power!'.format(guild.name))
        # Sync the commands for the guild.
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild = guild)
        logging.info('Synced commands for {0}.'.format(guild.name))
        # Send a message when the command tree is synced.
        general = find(lambda x: x.name == 'general',  guild.text_channels)
        if general and general.permissions_for(guild.me).send_messages:
            await general.send('Enhanced {} with my magic power!'.format(guild.name))

    async def setup_hook(self):
        # Load the cogs.
        await cogs.load_cogs(self)

# Configure the logging.
logging.basicConfig(filename="logs/alpha.log", level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
# Intents for the bot.
intents = discord.Intents.none()
intents.messages = True
intents.guilds = True
# Description for the bot.
description = '''Alpha testing.'''
# Create the bot.
bot = AlphaBot(command_prefix='!', description=description, intents=intents)

# Read the token from the token file.
with open('secrets/token', 'r') as f:
    token = f.read()
f.close()
# Run the bot.
bot.run(token)