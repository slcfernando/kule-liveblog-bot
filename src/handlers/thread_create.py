from discord import Client, Thread

from services import sheets

def setup(client: Client):
    @client.event
    async def on_thread_create(thread: Thread):
        if thread.parent.name == 'kule-liveblog-bot-test':
            print(f'Thread {thread.name} was created')

            # Create new sheet in the spreadsheet using the thread's name
            service = sheets.connect_to_sheets_api()
            sheets.create_sheet(service, thread.name)
