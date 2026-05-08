import discord
import os
from dotenv import load_dotenv
from handlers import thread_create

# Setup bot
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
# if BOT_TOKEN is not str:
#     raise ValueError('BOT_TOKEN not in .env file')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# When bot is ready
@client.event
async def on_ready():
    print(f'{client.user} is ready for live blogging')

if __name__ == '__main__':
    # Setup client using setup functions of each handler
    thread_create.setup(client)

    client.run(BOT_TOKEN)