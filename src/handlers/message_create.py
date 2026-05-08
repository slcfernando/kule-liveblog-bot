import os
from dotenv import load_dotenv
from discord import Client, Message
from googleapiclient.discovery import Resource

from services import sheets

load_dotenv()
LIVE_BLOG_FORUM_NAME = os.getenv('LIVE_BLOG_FORUM_NAME')

def setup(client: Client, service: Resource):
    @client.event
    async def on_message(message: Message):
        print(f'A message was sent: {message}')
        # Ignore messages not sent in a live blog forum post (which is a thread)
        channel = message.channel
        if not channel or not channel.parent or channel.parent.name != LIVE_BLOG_FORUM_NAME:
            print(f'The message was sent in {channel.parent.name} and not {LIVE_BLOG_FORUM_NAME}')
            return
    
        try:        
            # Create new row in the spreadsheet containing the contents of the message sent
            sheets.add_sheet_entry(service, channel.name, message)
        except Exception as e:
            print(f'An error occured: {e}')
            await channel.send('An error occurred while creating a new entry on the Google Sheet.')