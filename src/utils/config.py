import os
from dotenv import load_dotenv

# Setup environment variables
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

LIVE_BLOG_FORUM_NAME = os.getenv('LIVE_BLOG_FORUM_NAME')

GOOGLE_SHEETS_API_JSON_FILE_PATH = os.getenv('GOOGLE_SHEETS_API_JSON_FILE_PATH')
GOOGLE_SPREADSHEET_ID = os.getenv('GOOGLE_SPREADSHEET_ID')