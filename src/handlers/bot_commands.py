from discord import TextChannel, StageChannel, VoiceChannel, Thread, DMChannel, GroupChannel, PartialMessageable

Channel = TextChannel | StageChannel | VoiceChannel | Thread | DMChannel | GroupChannel | PartialMessageable

READY_MESSAGE = 'I\'m ready for live blogging! 😁'

HELP_MESSAGE = \
"""# [Access the Kulê Live Blogs GSheet here](https://docs.google.com/spreadsheets/d/1U9kR7ElhsyPal-fzv8bF7JUj2StGojfEiRY7kBpIt7Q/edit?gid=967854119).

# How to use the live blog bot:
- Type `$ready` in any public thread to confirm that I'm active. If not, @/Sidney.
- Create a **public forum post** in https://discord.com/channels/1391794809987010560/1418824817276227655 that starts with `[LIVE]` to create a new sheet in the live blog spreadsheet.
- Send messages in the `[LIVE]` post so they get added to the sheet for editing. No need to tag an editor.
- For communications, create a separate forum post that has the same name but starts with `[COMMS]`.
"""

async def ready(channel: Channel):
    try:
        await channel.send(READY_MESSAGE)
    except Exception as e:
        print(f'An error occurred while the bot tried to send a message: {e}')

async def help(channel: Channel):
    try:
        await channel.send(HELP_MESSAGE)
    except Exception as e:
        print(f'An error occurred while the bot tried to send a message: {e}')