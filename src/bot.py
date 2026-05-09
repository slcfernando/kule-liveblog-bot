import discord
from handlers import thread_create, message_create

from services import sheets
from utils.config import BOT_TOKEN

# Setup bot
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Connect to Google Sheets API
service = sheets.authenticate_sheets_api()

# When bot is ready
@client.event
async def on_ready():
    print(f'{client.user} is ready for live blogging')

if __name__ == '__main__':
    # Setup client using setup functions of each handler
    thread_create.setup(client, service)
    message_create.setup(client, service)

    client.run(BOT_TOKEN)