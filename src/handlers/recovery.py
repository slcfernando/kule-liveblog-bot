import discord
from discord import Client, TextChannel, Thread
from googleapiclient.discovery import Resource

from services import sheets
from utils import live
from utils.config import DISCORD_COVERAGES_NAME


async def recover_missed_messages(client: Client, service: Resource) -> None:
    print("Recovery function called.")
    for guild in client.guilds:
        coverages_channel = discord.utils.get(
            guild.channels, name=DISCORD_COVERAGES_NAME
        )

        if coverages_channel is None:
            print(
                f"Coverages channel with name {DISCORD_COVERAGES_NAME} was not found in guild {guild.name}."
            )
            continue

        if not isinstance(coverages_channel, TextChannel):
            print(
                f"Coverages channel with name {coverages_channel.name} is not a TextChannel."
            )
            continue

        active_threads = await guild.active_threads()
        print(f"Fetched {len(active_threads)} active threads: {active_threads = }")
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
        print(
            f"An error occurred while getting the last message ID in thread {thread.name}: {e}"
        )
        return

    after_snowflake = (
        discord.Object(id=int(last_message_id)) if last_message_id is not None else None
    )
    missed_messages = []

    try:
        async for message in thread.history(
            limit=None, after=after_snowflake, oldest_first=True
        ):
            if message.author == client.user:
                print(f"Skipped own bot message: {message.content}")
                continue
            missed_messages.append(message)
    except Exception as e:
        print(
            f"An error occurred while getting missed messages in thread {thread.name}: {e}"
        )
        return

    if not missed_messages:
        return

    recovered_count = 0
    for message in missed_messages:
        try:
            # Skip messages that mention users
            if live.is_mention_only(message):
                continue

            existing_row = sheets.find_row_by_message_id(
                service, thread.name, str(message.id)
            )
            if existing_row is not None:
                await message.add_reaction("✅")
                continue

            sheets.add_sheet_entry(service, thread.name, message)
            await message.add_reaction("✅")
            recovered_count += 1
        except Exception as e:
            print(f"An error occurred while adding a sheet entry: {e}")

    if recovered_count > 0:
        await thread.send(
            f"The bot was offline. {recovered_count} previous message/s have been added to the Google Sheet."
        )
