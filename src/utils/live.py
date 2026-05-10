def is_live_thread(name: str) -> bool:
    return name.strip().startswith("[LIVE]")
