from discord import Client, Message, Thread
from googleapiclient.discovery import Resource

from services import sheets
from utils import live

def setup(client: Client, service: Resource):
    @client.event
    async def on_message(message: Message):
        # Ignore messages sent by the bot itself.
        if message.author == client.user:
            return
        
        print(f'A message was sent: {message}')
        # Ignore messages not sent in a live blog forum post (which is a thread)
        channel = message.channel
        if not (isinstance(channel, Thread) and
                live.is_live_thread(channel.name)):
            print('Message not sent in a [LIVE] forum post')
            return
    
        try:        
            # Create new row in the spreadsheet containing the contents of the message sent
            sheets.add_sheet_entry(service, channel.name, message)
        except Exception as e:
            print(f'An error occured: {e}')
            await channel.send('An error occurred while creating a new entry on the Google Sheet.')