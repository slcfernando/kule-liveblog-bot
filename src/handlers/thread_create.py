import os
from dotenv import load_dotenv
from discord import Client, Thread
from googleapiclient.discovery import Resource

from services import sheets

load_dotenv()
LIVE_BLOG_FORUM_NAME = os.getenv('LIVE_BLOG_FORUM_NAME')

def setup(client: Client, service: Resource):
    @client.event
    async def on_thread_create(thread: Thread):
        try:        
            # Verify that forum is the one for live blogs
            if thread.parent.name == LIVE_BLOG_FORUM_NAME:
                # Create new sheet in the spreadsheet using the thread's name
                sheets.create_sheet(service, thread.name)
                sheets.initialize_sheet(service, thread.name, thread.jump_url)
        except Exception as e:
            print(f'An error occured: {e}')
            await thread.send('An error occurred while setting up this live coverage\'s Google Sheet.')