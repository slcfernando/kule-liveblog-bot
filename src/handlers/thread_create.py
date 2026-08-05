import discord
from discord import Client, TextChannel, Thread
from googleapiclient.discovery import Resource

from handlers import bot_commands
from services import sheets
from utils import live


def setup(client: Client, service: Resource):
    @client.event
    async def on_thread_create(thread: Thread):
        try:
            # Verify that forum post is one for live coverage
            if not live.is_live_thread(thread.name):
                print(f"Thread {thread.name} is not a [LIVE] thread.")
                return
            
            # Create new sheet in the spreadsheet using the thread's name
            sheet_id = sheets.create_sheet(service, thread.name)
            sheets.initialize_sheet(service, thread.name, thread.jump_url, sheet_id)

            # Create [COMMS] thread
            parent = thread.parent
            if not isinstance(parent, TextChannel):
                print(f"Parent of {thread.name} is not a TextChannel. Skipping [COMMS] thread creation.")
                return

            comms_name = live.get_paired_comms_name(thread.name)
            comms_thread = await parent.create_thread(
                name=comms_name,
                type=discord.ChannelType.public_thread,
            )
            await comms_thread.send(f"This is the COMMS thread for {thread.jump_url}.")

            # Send instructions to the [LIVE] thread
            await bot_commands.send_live_instructions(thread, comms_thread.jump_url)

        except Exception as e:
            print(f"An error occured: {e}")
            await thread.send(
                "An error occurred while setting up this live coverage's Google Sheet."
            )
