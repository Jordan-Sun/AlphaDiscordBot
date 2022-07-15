import os
import logging

from discord.ext import commands

# List of cogs to load
cogs = []

# Import all the cogs
for module in os.listdir(os.path.dirname(__file__)):
    if module == '__init__.py' or module[-3:] != '.py':
        # Ignore this file
        continue
    # Import the module
    exec('from .{} import *'.format(module[:-3]))
    cogs.append(module[:-3])

async def load_cogs(bot: commands.Bot):
    for cog in cogs:
        await eval('bot.add_cog({}.{}Cog(bot))'.format(cog, cog))
        logging.info('Loaded {} cog'.format(cog))