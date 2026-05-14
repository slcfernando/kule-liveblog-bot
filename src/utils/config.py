import os

from dotenv import load_dotenv

# Setup environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if BOT_TOKEN is None:
    raise RuntimeError("BOT_TOKEN absent from .env")

GOOGLE_SHEETS_API_JSON_FILE_PATH = os.getenv("GOOGLE_SHEETS_API_JSON_FILE_PATH")
if GOOGLE_SHEETS_API_JSON_FILE_PATH is None:
    raise RuntimeError("GOOGLE_SHEETS_API_JSON_FILE_PATH absent from .env")

GOOGLE_SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID")
if GOOGLE_SPREADSHEET_ID is None:
    raise RuntimeError("GOOGLE_SPREADSHEET_ID absent from .env")

GOOGLE_SPREADSHEET_LINK = os.getenv("GOOGLE_SPREADSHEET_LINK")
if GOOGLE_SPREADSHEET_LINK is None:
    raise RuntimeError("GOOGLE_SPREADSHEET_LINK absent from .env")

DISCORD_COVERAGES_FORUM = os.getenv("DISCORD_COVERAGES_FORUM")
if DISCORD_COVERAGES_FORUM is None:
    raise RuntimeError("DISCORD_COVERAGES_FORUM absent from .env")