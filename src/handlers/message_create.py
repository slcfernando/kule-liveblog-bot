from discord import Client, Message, Thread
from googleapiclient.discovery import Resource

from handlers import bot_commands
from services import sheets
from utils import live


async def _find_thread_by_name(
    guild_threads: list[Thread], name: str
) -> Thread | None:
    for thread in guild_threads:
        if thread.name == name:
            return thread
    return None


def setup(client: Client, service: Resource):
    @client.event
    async def on_message(message: Message):
        # Ignore messages sent by the bot itself.
        if message.author == client.user:
            return

        print(f"A message was sent: {message}")

        channel = message.channel

        # Confirm if the bot is active
        if message.content == "$ready":
            await bot_commands.test(channel)
            return

        # Help for how to use the bot
        if message.content == "$help":
            await bot_commands.help(channel)
            return

        is_live = live.is_live_thread(channel.name)
        is_comms = live.is_comms_thread(channel.name)

        # Ignore messages not sent in a live or comms thread
        if not (is_live or is_comms):
            print("Message not sent in a [LIVE] or [COMMS] forum post")
            return

        active_threads = await message.guild.active_threads()

        if is_live:
            await _handle_live_message(message, channel, active_threads, service, client)
        elif is_comms:
            await _handle_comms_message(message, channel, active_threads, client)


async def _handle_live_message(
    message: Message,
    channel: Thread,
    active_threads: list[Thread],
    service: Resource,
    client: Client
):
    if live.is_mention_only(message):
        comms_name = live.get_paired_comms_name(channel.name)
        comms_thread = await _find_thread_by_name(active_threads, comms_name)
        if comms_thread is None:
            print(f"[COMMS] thread {comms_thread.name} could not be found.")
            return

        mention_list = " ".join(m.mention for m in message.mentions)
        # Include the actual message sender in the mention list.
        mention_list += f" {message.author}"
        await comms_thread.send(f"Adding {mention_list} from **{channel.name}**")
        print(f"Relayed mentions to [COMMS] thread {comms_name}")
        return

    try:
        sheets.add_sheet_entry(service, channel.name, message)
    except Exception as e:
        print(f"Error adding sheet entry: {e}")
        await channel.send(
            "An error occurred while creating a new entry on the Google Sheet."
        )


async def _handle_comms_message(
    message: Message,
    channel: Thread,
    active_threads: list[Thread],
    client: Client
) -> None:
    if not message.mentions:
        print(f"Message with content {message.content} has no mentions.")
        return

    live_name = live.get_paired_live_name(channel.name)
    live_thread = await _find_thread_by_name(active_threads, live_name)
    if live_thread is None:
        print(f"Could not find [LIVE] thread with name {live_name}.")
        return

    for member in message.mentions:
        try:
            await live_thread.add_user(member)
            print(f"Added {member.name} to {live_name} from mention in {channel.name}.")
        except Exception as e:
            print(f"Failed to add {member.name} to {live_name}: {e}")