# import re
from discord import Message


def is_live_thread(name: str) -> bool:
    return name.strip().startswith("[LIVE]")

def is_comms_thread(name: str) -> bool:
    return name.strip().startswith("[COMMS]")

def get_paired_comms_name(live_name: str) -> str:
    event_name = live_name.strip()[len("[LIVE]"):].strip()
    return f"[COMMS] {event_name}"

def get_paired_live_name(comms_name: str) -> str:
    event_name = comms_name.strip()[len("[COMMS]"):].strip()
    return f"[LIVE] {event_name}"

def is_mention_only(message: Message) -> bool:
    # TODO: For now, we assume that a message that has any form of mention will be skipped
    if not message.mentions and not message.role_mentions:
        print(f"Message with content {message.content} has no mentions.")
        return False
    # content = re.sub(r"<@!?\d+>", "", message.content)
    # content = re.sub(r"<@&\d+>", "", content)
    # content = re.sub(r"<#\d+>", "", content)

    return True