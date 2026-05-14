from discord import Client, Message, Thread
from googleapiclient.discovery import Resource

from handlers import bot_commands
from services import sheets
from utils import live


def setup(client: Client, service: Resource):
    @client.event
    async def on_message(message: Message):
        # Ignore messages sent by the bot itself.
        if message.author == client.user:
            return

        print(f"A message was sent: {message}")

        # Confirm if the bot is active
        channel = message.channel
        if message.content == '$ready':
            await bot_commands.ready(channel)
            return

        # Help for how to use the bot
        channel = message.channel
        if message.content == '$help':
            await bot_commands.help(cwhannel)
            return

        # Ignore messages not sent in a live blog forum post (which is a thread)
        if not (isinstance(channel, Thread) and live.is_live_thread(channel.name)):
            print("Message not sent in a [LIVE] forum post")
            return

        try:
            # Create new spreadsheet row containing contents of message sent
            sheets.add_sheet_entry(service, channel.name, message)
        except Exception as e:
            print(f"An error occured: {e}")
            await channel.send(
                "An error occurred while creating a new entry on the Google Sheet."
            )
