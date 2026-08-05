import discord
from discord import Client, TextChannel, Thread
from googleapiclient.discovery import Resource

from services import sheets
from utils import live
from utils.config import DISCORD_COVERAGES_NAME


async def recover_missed_messages(client: Client, service: Resource) -> None:
    for guild in client.guilds:
        coverages_channel = discord.utils.get(
            guild.channels, name=DISCORD_COVERAGES_NAME
        )

        if coverages_channel is None:
            print(f"Coverages channel with name {DISCORD_COVERAGES_NAME} was not found in guild {guild.name}.")
            continue

        if not isinstance(coverages_channel, TextChannel):
            print(f"Coverages channel with name {coverages_channel.name} is not a TextChannel.")
            continue

        active_threads = await guild.active_threads() 
        for thread in active_threads:
            if thread.parent_id != coverages_channel.id:
                continue
            if not live.is_live_thread(thread.name):
                print(f"Thread with name {thread.name} is not a live thread.")
                continue
            await _recover_thread(thread, service, client)


async def _recover_thread(thread: Thread, service: Resource, client: Client):
    try:
        last_message_id = sheets.get_last_message_id(service, thread.name)
    except Exception as e:
        print(f"An error occurred while getting the last message ID in thread {thread.name}: {e}")
        return

    if last_message_id is None:
        return

    after_snowflake = discord.Object(id=int(last_message_id))
    missed_messages = []

    try:
        async for message in thread.history(
            limit=100, after=after_snowflake, oldest_first=True
        ):
            if message.author == client.user:
                missed_messages.append(message)
                continue
    except Exception as e:
        print(f"An error occurred while getting missed messages in thread {thread.name}: {e}")
        return

    if not missed_messages:
        return

    recovered_count = 0
    for message in missed_messages:
        try:
            sheets.add_sheet_entry(service, thread.name, message)
            # TODO: It would be nice if the bot reacts to messages that are added to the sheet
            recovered_count += 1
        except Exception as e:
            print(f"An error occurred while adding a sheet entry: {e}")
            pass

    await thread.send(
        f"The bot was offline. {recovered_count} previous message/s have been added to the Google Sheet."
    )
