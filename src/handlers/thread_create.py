import os
from dotenv import load_dotenv
from discord import Client, Thread
from discord.channel import ForumChannel
from googleapiclient.discovery import Resource

from services import sheets

load_dotenv()
LIVE_BLOG_FORUM_NAME = os.getenv('LIVE_BLOG_FORUM_NAME')

def setup(client: Client, service: Resource):
    @client.event
    async def on_thread_create(thread: Thread):
        print(f'New thread was created with name {thread}')
        
        # Verify that forum is the one for live blogs
        if thread.parent.name == LIVE_BLOG_FORUM_NAME:
            # Create new sheet in the spreadsheet using the thread's name
            sheets.create_sheet(service, thread.name)
            sheets.initialize_sheet(service, thread.name, thread.jump_url)
