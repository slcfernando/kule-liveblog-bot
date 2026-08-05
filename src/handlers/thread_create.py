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
            comms_instructions = await comms_thread.send(bot_commands.COMMS_INSTRUCTIONS.replace("<LIVE URL>", thread.jump_url))

            # Pin [COMMS] instructions
            await comms_instructions.pin()

            # Mention [LIVE] thread creator in [COMMS]
            await comms_thread.send(f"Adding [LIVE] thread creator @{thread.owner}.")

            # Send instructions to the [LIVE] thread
            live_instructions = await bot_commands.send_live_instructions(thread, comms_thread.jump_url)
            if live_instructions:
                await live_instructions.pin()

        except Exception as e:
            print(f"An error occured: {e}")
            await thread.send(
                "An error occurred while setting up this live coverage's Google Sheet."
            )
