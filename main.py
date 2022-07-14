import Bot

import discord

async def main():
    # Set up discord bot intent.
    intents = discord.Intents.default()
    # Create duscord bot client.
    client = Bot(intents=intents)
    # Read discord bot token.
    with open('token', 'r') as file:
        token = file.read()
    # Run discord bot client.
    client.run(token)