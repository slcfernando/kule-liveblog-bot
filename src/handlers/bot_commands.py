from discord import (
    DMChannel,
    GroupChannel,
    Message,
    PartialMessageable,
    StageChannel,
    TextChannel,
    Thread,
    VoiceChannel,
)

from utils.config import DISCORD_COVERAGES_FORUM, GOOGLE_SPREADSHEET_LINK

Channel = (
    TextChannel
    | StageChannel
    | VoiceChannel
    | Thread
    | DMChannel
    | GroupChannel
    | PartialMessageable
)

READY_MESSAGE = "I'm ready for live blogging! 😁"

HELP_MESSAGE = (
    f"# [Access the Kulê Live Blogs GSheet here]({GOOGLE_SPREADSHEET_LINK}).\n"
    "# How to use the live blog bot:\n"
    "- Type `$ready` in any public thread to confirm that I'm active. "
    "If not, @/Sidney.\n"
    "- Create a **public thread** in "
    f"{DISCORD_COVERAGES_FORUM} that starts "
    "with `[LIVE]` to create a new sheet in the live blog spreadsheet.\n"
    "- Send messages in the `[LIVE]` thread so they get added to the sheet for editing. "
    "Do not tag an editor.\n"
    "- For communications, the bot will automatically create a partner thread that starts with [COMMS].\n"
    "- Tag any person in [LIVE] and they will be added to [COMMS] automatically (and vice versa)."
)

LIVE_INSTRUCTIONS = """**Do not send anything here other than posts for editing.** Posts will automatically appear [here](https://discord.com/channels/1525773509698256928/1532688580307324939/1532767729881321754). All communications should be done via <COMMS URL>.
# Instructions:
- All posts longer than 100 words must be accompanied by a headline (format is sentence case, ending with a period) and appropriate media (images by default, but videos, other visualizations, etc. may be deemed acceptable). The said media should appear before the body text.
- All prewrites must be moved to this thread prior to the moment the live blog opens.
- **For the remote member running the blog:** When publishing to the platform, make sure to paste the contents as plain text, remove all extra line breaks, and download all photos before uploading.
- Edit the pinned briefing periodically. Switch from the opener (_"Here's what you need to know."_) to the _"Here's the latest."_ bulleted summary format once the blog is rolling.
- Upload all videos to X first before embedding.
- For short entries that contain media, the photo/video comes after the post's body text and an extra line break.
"""


COMMS_INSTRUCTIONS = """Use this COMMS thread for communications. Send posts for editing in <LIVE URL>. 
"""


async def ready(channel: Channel):
    try:
        await channel.send(READY_MESSAGE)
    except Exception as e:
        print(f"An error occurred while the bot tried to send a message: {e}")


async def help(channel: Channel):
    try:
        await channel.send(HELP_MESSAGE)
    except Exception as e:
        print(f"An error occurred while the bot tried to send a message: {e}")


async def test(channel: Channel):
    try:
        await channel.send(
            "Maayong adlaw UP Mindanao! <:vyansablay:1526094164700168253>"
        )
    except Exception as e:
        print(f"An error occurred while the bot tried to send a message: {e}")


async def send_live_instructions(thread: Thread, comms_url: str) -> Message | None:
    try:
        live_instructions = await thread.send(
            LIVE_INSTRUCTIONS.replace("<COMMS URL>", comms_url)
        )
        return live_instructions
    except Exception as e:
        print(f"Failed to send instructions to {thread.name}: {e}")
        return
