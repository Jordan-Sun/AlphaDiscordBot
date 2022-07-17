import io
import logging
import os.path
from typing import OrderedDict, Tuple, Callable

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import discord
from discord import app_commands
from discord.ext import commands

class sheetsCog(commands.Cog):
    # Constructor for the cog.
    def __init__(self, bot: commands.Bot, scopes: list[str] = ['https://www.googleapis.com/auth/spreadsheets']) -> None:
        self.bot = bot
        self.scopes = scopes
        self.creds = self.__get_credentials()
        self.service = self.__get_service(self.creds)
        self.sheet_id = self.__get_sheet_id()

    def __get_credentials(self) -> Credentials:
        # Gets the credentials for the Google API.
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('secrets/token.json'):
            with open('secrets/token.json', 'rb') as token:
                creds = Credentials.from_authorized_user_file('secrets/token.json', self.scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'secrets/credentials.json', self.scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('secrets/token.json', 'w') as token:
                token.write(creds.to_json())
        # Return the credentials.
        return creds

    def __get_service(self, creds: Credentials) -> Callable:
        # Gets the service for the Google API.
        try:
            service = build('sheets', 'v4', credentials=creds)
            return service
        except HttpError as err:
            logging.error(err)
    
    def __get_sheet_id(self) -> str:
        # Get the spreadsheet ID from the file.
        with open('secrets/sheet_id', 'r') as f: 
            sheet_id = f.read()
        f.close()
        return sheet_id
    
    def __get_sheet(self, range: str) -> list[list[str]]:
        # Gets the sheet from the spreadsheet.
        sheet = self.service.spreadsheets().values().get(spreadsheetId=self.sheet_id, range=range)
        result = sheet.execute()
        return result.get('values', [])
    
    def __get_sheet_all(self, guild: discord.Guild):
        # Gets the entire sheet from the spreadsheet.
        return self.__get_sheet(str(guild.id))

    def __get_sheet_header(self, guild: discord.Guild):
        # Gets the header from the spreadsheet.
        return self.__get_sheet(str(guild.id) + '!1:1')[0]
    
    def __get_sheet_data(self, guild: discord.Guild) -> list[list[str]]:
        # Gets the data from the spreadsheet.
        return self.__get_sheet(str(guild.id))[1:]
    
    def __update_sheet(self, range: str, values: list[list[str]], vaule_input_option: str = 'USER_ENTERED') -> None:
        # Updates the sheet with the vault input option.
        sheet = self.service.spreadsheets().values().update(spreadsheetId=self.sheet_id, range=range, body={'values': values}, valueInputOption=vaule_input_option)
        sheet.execute()
    
    def __update_sheet_all(self, guild: discord.Guild, data: list[list[str]]) -> None:
        # Updates the entire sheet.
        self.__update_sheet(str(guild.id), data)

    def __update_sheet_header(self, guild: discord.Guild, header: list[str]) -> None:
        # Updates the header in the spreadsheet.
        self.__update_sheet(str(guild.id) + '!1:1', [header])
    
    def __update_sheet_data(self, guild: discord.Guild, data: list[list[str]]) -> None:
        # Updates the data in the spreadsheet.
        header = self.__get_sheet_header(guild)
        data.insert(0, header)
        self.__update_sheet(str(guild.id), data)
    
    def __append_sheet(self, range: str, values: list[list[str]]) -> None:
        # Appends the data to the spreadsheet.
        sheet = self.service.spreadsheets().values().append(spreadsheetId=self.sheet_id, range=range, body={'values': values}, valueInputOption='USER_ENTERED', insertDataOption='INSERT_ROWS')
        sheet.execute()

    def __append_sheet_row(self, guild: discord.Guild, row: list[str]) -> None:
        # Appends a row to the spreadsheet.
        self.__append_sheet(str(guild.id), [row])

    @staticmethod
    def __is_sheet_manager(member: discord.Member) -> bool:
        # If the member is an administrator, return true.
        if member.guild_permissions.administrator:
            return True
        # If the member has the role, return true.
        for role in member.roles:
            if role.name == 'Sheet Manager':
                return True
        # Otherwise, return false.
        return False

    # /add command
    @app_commands.command(name="add", description="add a new member")
    async def add(self, interaction: discord.Interaction, name: str) -> None:
        # Check if the user has the role.
        if not sheetsCog.__is_sheet_manager(interaction.user):
            await interaction.response.send_message("You do not have the permission for managing the sheet.", ephemeral=True)
            return
        # Check if the name is in the sheet.
        sheet = self.__get_sheet_data(interaction.guild)
        for row in sheet:
            if row and row[0] == name:
                # If the name is in the sheet, send error message.
                await interaction.response.send_message("The member is already in the sheet.", ephemeral=True)
                return
        # Otherwise, add the name to the sheet.
        self.__append_sheet_row(interaction.guild, [name])
        await interaction.response.send_message("The member has been added to the sheet.", ephemeral=True)
        return

    # /remove command
    @app_commands.command(name="remove", description="remove a member")
    async def remove(self, interaction: discord.Interaction, name: str) -> None:
        # Check if the user has the role.
        if not sheetsCog.__is_sheet_manager(interaction.user):
            await interaction.response.send_message("You do not have the permission for managing the sheet.", ephemeral=True)
            return
        # Check if the name is in the sheet.
        sheet = self.__get_sheet_data(interaction.guild)
        newsheet = []
        found = 0
        for row in sheet:
            if row and row[0] == name:
                # If is the name, skip it.
                found += 1
            else:
                # If not the name, add the row to the new sheet.
                newsheet.append(row)
        if found:
            # If the name is in the sheet, remove the name from the sheet.
            for _ in range(found):
                newsheet.append([''])
            self.__update_sheet_data(interaction.guild, newsheet)
            await interaction.response.send_message("Removed the member from the sheet.", ephemeral=True)
        else:
            # Otherwise, send error message.
            await interaction.response.send_message("Could not find the member in the sheet.", ephemeral=True)
        return

    @staticmethod
    def __row_to_string(row: list[str]) -> str:
        # Converts a row to a string.
        return ',\t'.join(row)

    @staticmethod
    def __sheet_to_string(sheet: list[list[str]]) -> str:
        # Converts a sheet to a string.
        return ',\n'.join([sheetsCog.__row_to_string(row) for row in sheet])

    # /new command
    @app_commands.command(name="new", description="create a new attribute")
    async def new(self, interaction: discord.Interaction, attribute: str) -> None:
        # Check if the user has the role.
        if not sheetsCog.__is_sheet_manager(interaction.user):
            await interaction.response.send_message("You do not have the permission for managing the sheet.", ephemeral=True)
            return
        # Check if the attribute is in the sheet.
        header = self.__get_sheet_header(interaction.guild)
        if attribute in header:
            # If the attribute is in the sheet, send error message.
            await interaction.response.send_message("The attribute is already in the sheet.", ephemeral=True)
            return
        # Otherwise, add the attribute to the sheet.
        self.__update_sheet_header(interaction.guild, header + [attribute])
        await interaction.response.send_message("The attribute has been added to the sheet.", ephemeral=True)
        return
    
    # /delete command
    @app_commands.command(name="delete", description="delete an attribute")
    async def delete(self, interaction: discord.Interaction, attribute: str) -> None:
        # Check if the user has the role.
        if not sheetsCog.__is_sheet_manager(interaction.user):
            await interaction.response.send_message("You do not have the permission for managing the sheet.", ephemeral=True)
            return
        # Check if the attribute is Name.
        if attribute == 'Name':
            # If the attribute is Name, send error message.
            await interaction.response.send_message("The attribute is reserved.", ephemeral=True)
            return
        # Check if the attribute is in the sheet.
        header = self.__get_sheet_header(interaction.guild)
        if attribute not in header:
            # If the attribute is not in the sheet, send error message.
            await interaction.response.send_message("The attribute is not in the sheet.", ephemeral=True)
            return
        # Otherwise, remove the attribute from the sheet.
        index = header.index(attribute)
        sheet = self.__get_sheet_all(interaction.guild)
        newsheet = []
        for row in sheet:
            newsheet.append(row[:index] + row[index+1:] + [''])
        self.__update_sheet_all(interaction.guild, newsheet)
        await interaction.response.send_message("The attribute has been removed from the sheet.", ephemeral=True)
        return

    # /edit command
    @app_commands.command(name="edit", description="edit the attribute of a member")
    async def edit(self, interaction: discord.Interaction, name: str, attribute: str, value: str) -> None:
        # Check if the user has the role.
        if not sheetsCog.__is_sheet_manager(interaction.user):
            await interaction.response.send_message("You do not have the permission for managing the sheet.", ephemeral=True)
            return
        # Check if the name is in the sheet.
        header = self.__get_sheet_header(interaction.guild)
        sheet = self.__get_sheet_data(interaction.guild)
        if attribute not in header:
            # If the attribute is not in the sheet, send error message.
            await interaction.response.send_message("The attribute is not in the sheet.", ephemeral=True)
            return
        for row in sheet:
            if row and row[0] == name:
                # If the name is in the sheet, edit the attribute.
                row[header.index(attribute)] = value
                self.__update_sheet_data(interaction.guild, sheet)
                await interaction.response.send_message("The attribute has been edited.", ephemeral=True)
                return
        # Otherwise, send error message.
        await interaction.response.send_message("Could not find the member in the sheet.", ephemeral=True)
        return

    # /multiedit command
    @app_commands.command(name="multiedit", description="edit the attributes of a member, separated by commas, use '~' to represent an unchanged value")
    async def multiedit(self, interaction: discord.Interaction, name: str, attributes: str) -> None:
        # Check if the user has the role.
        if not sheetsCog.__is_sheet_manager(interaction.user):
            await interaction.response.send_message("You do not have the permission for managing the sheet.", ephemeral=True)
            return
        # Check if the name is in the sheet.
        sheet = self.__get_sheet_data(interaction.guild)
        attributes_row = attributes.split(',')
        for row in sheet:
            if row and row[0] == name:
                # If the name is in the sheet, edit the attribute.
                for index in range(len(attributes_row)):
                    # If the new value is '~', do not change the value.
                    if attributes_row[index] == '~':
                        continue
                    # If the new value is not '~', edit the attribute.
                    row[index+1] = attributes_row[index]
                self.__update_sheet_data(interaction.guild, sheet)
                await interaction.response.send_message("Attributes have been edited.", ephemeral=True)
                return
        # Otherwise, send error message.
        await interaction.response.send_message("Could not find the member in the sheet.", ephemeral=True)
        return

    async def __send_long_message(self, interaction: discord.Interaction, message: str, ephemeral: bool = True) -> None:
        # Send a long message as an attachment instead.
        await interaction.response.send_message("Message sent as attachment instead.", file=discord.File(io.StringIO(message), filename="tmp.txt"), ephemeral=ephemeral)
        return

    # /list command
    @app_commands.command(name="list", description="list all members")
    async def list(self, interaction: discord.Interaction, ephemeral: bool = True) -> None:
        # Check if the user has the role.
        if not sheetsCog.__is_sheet_manager(interaction.user):
            await interaction.response.send_message("You do not have the permission for managing the sheet.", ephemeral=True)
            return
        # Get the sheet data.
        sheet = self.__get_sheet_all(interaction.guild)
        # Send the sheet data.
        await self.__send_long_message(interaction, sheetsCog.__sheet_to_string(sheet), ephemeral)
        return

    # /attributes command
    @app_commands.command(name="attributes", description="list all attributes")
    async def attributes(self, interaction: discord.Interaction, ephemeral: bool = True) -> None:
        # Check if the user has the role.
        if not sheetsCog.__is_sheet_manager(interaction.user):
            await interaction.response.send_message("You do not have the permission for managing the sheet.", ephemeral=True)
            return
        # Get the sheet header.
        header = self.__get_sheet_header(interaction.guild)
        # Send the sheet header.
        await interaction.response.send_message(interaction, sheetsCog.__sheet_to_string(header), ephemeral)
        return

    # /show command
    @app_commands.command(name="show", description="show the info of a member")
    async def info(self, interaction: discord.Interaction, name: str, ephemeral: bool = True) -> None:
        # Check if the user has the role.
        if not sheetsCog.__is_sheet_manager(interaction.user):
            await interaction.response.send_message("You do not have the permission for managing the sheet.", ephemeral=True)
            return
        # Get the sheet data.
        sheet = self.__get_sheet_data(interaction.guild)
        # Find the name in the sheet.
        for row in sheet:
            if row and row[0] == name:
                # If the name is in the sheet, send the info.
                await self.__send_long_message(interaction, sheetsCog.__row_to_string(row), ephemeral)
                return
        