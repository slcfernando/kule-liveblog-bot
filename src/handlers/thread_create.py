import os
from dotenv import load_dotenv
from discord import Client, Thread, ForumChannel

from services import sheets

load_dotenv()
LIVE_BLOG_FORUM_NAME = os.getenv('LIVE_BLOG_FORUM_NAME')

def setup(client: Client):
    @client.event
    async def on_thread_create(thread: Thread):
        # Ignore threads not created in a forum
        if thread.parent is not ForumChannel:
            return
        
        # Verify that forum is the one for live blogs
        if thread.parent.name == LIVE_BLOG_FORUM_NAME:
            print(f'Thread {thread.name} was created')

            # Create new sheet in the spreadsheet using the thread's name
            service = sheets.connect_to_sheets_api()
            sheets.create_sheet(service, thread.name)
