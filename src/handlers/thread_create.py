from discord import Client, Thread
from googleapiclient.discovery import Resource

from services import sheets

def setup(client: Client, service: Resource):
    @client.event
    async def on_thread_create(thread: Thread):
        try:        
            # Verify that forum post is one for live coverage
            if thread.name.strip().startswith('[LIVE]'):
                # Create new sheet in the spreadsheet using the thread's name
                sheetId = sheets.create_sheet(service, thread.name)
                sheets.initialize_sheet(service, thread.name, thread.jump_url, sheetId)
        except Exception as e:
            print(f'An error occured: {e}')
            await thread.send('An error occurred while setting up this live coverage\'s Google Sheet.')