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

user_to_wallet_mapping = {}
user_xp = {}

@bot.command(name="register")
async def register(ctx, *args):
    wallet_addy = args[0]
    user_id = ctx.author.id
    user_to_wallet_mapping[user_id] = wallet_addy
    # this particular wallet address has to be now tracked

    ctx.send(f"<@{ctx.author.id}> has registered {wallet_addy}", ephermal = True)

@bot.command(name="xp")
async def xp(ctx):
    user_id = ctx.author.id
    try:
        user_xp[user_id]
    except KeyError:
        user_xp[user_id] = 0
    ctx.send(f"<@{ctx.author.id}> has {user_xp[user_id]} XP!")

@bot.command(name="unregister")
async def unregister(ctx):
    try:
        del user_to_wallet_mapping[ctx.author.id]
    except KeyError:
        pass
    ctx.send(f'<@{ctx.author.id}> has unregistered :(')

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

    

bot.run(TOKEN)