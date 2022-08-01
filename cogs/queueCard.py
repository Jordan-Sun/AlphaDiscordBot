from re import T
import discord
from discord import app_commands
from discord.ext import commands
from numpy import True_, tile

class queueCardButton(discord.ui.Button):
    def __init__(self, title: str, message: discord.Message, length: int = None):
        super().__init__(style=discord.ButtonStyle.secondary, label='Join/Leave')
        self.title = title
        self.message = message
        self.length = length
        self.members = []
    
    async def update(self) -> bool:
        if self.message is None:
            return False
        card = discord.Embed(title=self.title, color=0x00ff00)
        if self.members:
            if self.length is None:
                lengthText = f'Length: {len(self.members)}'
            else:
                lengthText = f'Length: {len(self.members)}/{self.length}'
            queueText = '\n'.join([f'{member.display_name}: {member.mention}' for member in self.members])
            card.add_field(name=lengthText, value=queueText, inline=False)
        await self.message.edit(embed=card)
        return True
    
    async def callback(self, interaction: discord.Interaction):
        if self.message is None:
            await interaction.response.send_message('Message is None', ephemeral=True)
            return
        for member in self.members:
            if member == interaction.user:
                self.members.remove(member)
                success = await self.update()
                if success:
                    await interaction.response.send_message(f'{interaction.user.mention} has left the queue.', ephemeral=True)
                else:
                    await interaction.response.send_message('Queue card not found.', ephemeral=True)
                return
        if self.length and len(self.members) >= self.length:
            await interaction.response.send_message('Queue is full.', ephemeral=True)
            return
        self.members.append(interaction.user)
        success = await self.update()
        if success:
            await interaction.response.send_message(f'{interaction.user.mention} has joined the queue.', ephemeral=True)
        else:
            await interaction.response.send_message('Queue card not found.', ephemeral=True)

class queueCardView(discord.ui.View):
    def __init__(self, title: str, message: discord.Message, length: int = None):
        super().__init__(timeout=None)
        self.add_item(queueCardButton(title=title, message=message, length=length))
    

class queueCardCog(commands.Cog):
    # Constructor for the cog.
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # /create command
    @app_commands.command(name="create", description="create a new queue card")
    async def ping(self, interaction: discord.Interaction, title: str, length: int = None) -> None:
        # Create a new queue card.
        message = await interaction.channel.send("Creating queue card...")
        card = discord.Embed(title=title, color=0x00ff00)
        view = queueCardView(title=title, message=message, length=length)
        await message.edit(content="", embed=card, view=view)
        await interaction.response.send_message("Created queue card.", ephemeral=True)