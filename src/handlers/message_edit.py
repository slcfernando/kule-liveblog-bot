from discord import Client, Message, Thread
from googleapiclient.discovery import Resource

from services import sheets
from utils import live

def setup(client: Client, service: Resource):
    @client.event
    async def on_message_edit(before: Message, after: Message):
        # Ignore messages sent by the bot itself.
        if after.author == client.user:
            return
        
        print(f'A message was edited: {after}')

        # Ignore messages not sent in a live blog forum post (which is a thread)
        channel = after.channel
        if not (isinstance(channel, Thread) and
                live.is_live_thread(channel.name)):
            print('Message not sent in a [LIVE] forum post')
            return
    
        try:
            sheets.edit_sheet_entry(service, channel.name, str(before.id), after)
        except Exception as e:
            print(f'An error occured: {e}')
            await channel.send('An error occurred while editing an entry on the Google Sheet.')