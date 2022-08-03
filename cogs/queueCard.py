import asyncio
import logging
import time
import discord
from discord import app_commands
from discord.ext import commands

class joinButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label='Join/Leave')

    async def callback(self, interaction: discord.Interaction):
        # Check if the user is in the queue
        for member in self.view.members:
            if member[0] == interaction.user:
                # Remove the user from the queue
                self.view.members.remove(member)
                success = self.view.update()
                if success:
                    await interaction.response.send_message(f'{interaction.user.mention} has left the queue.', ephemeral=True)
                else:
                    await interaction.response.send_message('Queue card not found.', ephemeral=True)
                return
        # Check if the queue is locked
        if self.view.locked:
            await interaction.response.send_message('This queue is locked.', ephemeral=True)
            return
        # Check if the queue is full
        if self.view.length and len(self.view.members) >= self.view.length:
            await interaction.response.send_message('Queue is full.', ephemeral=True)
            return
        # Add the user to the queue
        self.view.members.append((interaction.user, time.time()))
        # Update the queue card
        success = self.view.update()
        if success:
            await interaction.response.send_message(f'{interaction.user.mention} has joined the queue.', ephemeral=True)
        else:
            await interaction.response.send_message('Queue card not found.', ephemeral=True)

class lockButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label='Lock/Unlock')

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            self.view.locked = not self.view.locked
            success = self.view.update()
            if success:
                if self.view.locked:
                    await interaction.response.send_message('Queue is now locked.', ephemeral=True)
                else:
                    await interaction.response.send_message('Queue is now unlocked.', ephemeral=True)
            else:
                await interaction.response.send_message('Queue card not found.', ephemeral=True)
        else:
            await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True)
        
class clearButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label='Clear')

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            self.view.members = []
            success = self.view.update()
            if success:
                await interaction.response.send_message('Queue has been cleared.', ephemeral=True)
            else:
                await interaction.response.send_message('Queue card not found.', ephemeral=True)
        else:
            await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True)

""" class removeDropdown(discord.ui.Select):
    def __init__(self):
        options = []
        for position in range(len(self.view.members)):
            options.append(discord.SelectOption(label=self.view.members[position][0].display_name, value=position))
        super().__init__(placeholder='Remove', options=options)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            if self.view.members:
                self.view.members.pop(self.view.selected)
                success = self.view.update()
                if success:
                    await interaction.response.send_message('Member has been removed.', ephemeral=True)
                else:
                    await interaction.response.send_message('Queue card not found.', ephemeral=True)
            else:
                await interaction.response.send_message('Queue is empty.', ephemeral=True)
        else:
            await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True) """

class queueCardView(discord.ui.View):
    def __init__(self, title: str, message: discord.Message, length: int = None):
        super().__init__(timeout=None)
        self.title = title
        self.message = message
        self.length = length
        self.members = []
        self.locked = False
        self.always_show = [joinButton(), lockButton(), clearButton()]
        # self.constant_update = []
        self.update_scheduled = False
        for button in self.always_show:
            self.add_item(button)
    
    async def _update(self):
        if self.locked:
            title = f'{self.title} 🔒'
        else:
            title = f'{self.title}'
        card = discord.Embed(title=title, color=0x00ff00)
        if self.members:
            # for button in self.constant_update:
                # self.remove_item(button)
            # self.add_item(removeDropdown())

            if self.length is None:
                lengthText = f'Length: {len(self.members)}'
            else:
                lengthText = f'Length: {len(self.members)}/{self.length}'
            queueText = ''
            for position in range(len(self.members)):
                queueText += f'**{position+1}:** <t:{str(int(self.members[position][1]))}:t> {self.members[position][0].display_name} {self.members[position][0].mention}\n'
            card.add_field(name=lengthText, value=queueText, inline=False)
        await self.message.edit(embed=card)
        self.update_scheduled = False

    def update(self) -> bool:
        if self.message is None:
            return False
        elif not self.update_scheduled:
            self.update_scheduled = True
            asyncio.create_task(self._update())
        return True

    async def close(self):
        if self.message is not None:
            await self.message.delete()
            self.message = None
        super().close()
    

class queueCardCog(commands.Cog):
    # Constructor for the cog.
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # /create command
    @app_commands.command(name="create", description="create a new queue card")
    async def ping(self, interaction: discord.Interaction, title: str, length: int = None) -> None:
        # Create a new queue card.
        if interaction.user.guild_permissions.administrator:
            message = await interaction.channel.send("Creating queue card...")
            card = discord.Embed(title=title, color=0x00ff00)
            view = queueCardView(title=title, message=message, length=length)
            await message.edit(content="", embed=card, view=view)
            await interaction.response.send_message("Created queue card.", ephemeral=True)
        else:
            await interaction.response.send_message("You do not have permission to create a queue card.", ephemeral=True)