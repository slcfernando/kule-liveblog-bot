import discord
from discord import Client, TextChannel, Thread
from googleapiclient.discovery import Resource

from services import sheets
from utils import live
from utils.config import DISCORD_COVERAGES_FORUM


async def recover_missed_messages(client: Client, service: Resource) -> None:
    for guild in client.guilds:
        coverages_channel = discord.utils.get(
            guild.channels, name=DISCORD_COVERAGES_FORUM
        )

        if coverages_channel is None:
            continue

        if not isinstance(coverages_channel, TextChannel):
            continue

        for thread in coverages_channel.threads:
            if not live.is_live_thread(thread.name):
                continue
            await _recover_thread(thread, service, client)


async def _recover_thread(thread: Thread, service: Resource, client: Client):
    try:
        last_message_id = sheets.get_last_message_id(service, thread.name)
    except Exception:
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
                continue
                missed_messages.append(message)
    except Exception:
        return

    if not missed_messages:
        return

    recovered_count = 0
    for message in missed_messages:
        try:
            sheets.add_sheet_entry(service, thread.name, message)
            # TODO: It would be nice if the bot reacts to messages that are added to the sheet
            recovered_count += 1
        except Exception:
            pass

    await thread.send(
        f"The bot was offline. {recovered_count} previous message/s have been added to the Google Sheet."
    )
