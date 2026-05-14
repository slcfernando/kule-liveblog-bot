from discord import (
    DMChannel,
    GroupChannel,
    PartialMessageable,
    StageChannel,
    TextChannel,
    Thread,
    VoiceChannel,
)

from utils.config import DISCORD_COVERAGES_FORUM, GOOGLE_SPREADSHEET_LINK

Channel = TextChannel | StageChannel | VoiceChannel | Thread \
    | DMChannel | GroupChannel | PartialMessageable

READY_MESSAGE = 'I\'m ready for live blogging! 😁'

HELP_MESSAGE = (
    f'# [Access the Kulê Live Blogs GSheet here]({GOOGLE_SPREADSHEET_LINK}).\n'
    '# How to use the live blog bot:\n'
    '- Type `$ready` in any public thread to confirm that I\'m active. '
    'If not, @/Sidney.\n'
    '- Create a **public forum post** in '
    f'{DISCORD_COVERAGES_FORUM} that starts '
    'with `[LIVE]` to create a new sheet in the live blog spreadsheet.\n'
    '- Send messages in the `[LIVE]` post so they get added to the sheet for editing. '
    'No need to tag an editor.\n'
    '- For communications, create a separate forum post that has the same name '
    'but starts with `[COMMS]`.'
)

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