import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv, dotenv_values
import os

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    intents=intents)


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

    

bot.run(TOKEN)