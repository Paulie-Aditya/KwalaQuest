import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv, dotenv_values
import os
import requests
from flask import Flask, request, jsonify
import threading

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

GUILD_ID = 998879389007745085
TARGET_CHANNEL_ID = 1435639366818070540
intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True
BOT_PORT = int(os.getenv("BOT_PORT", 5001))
CHAIN_ID = 137  # Polygon mainnet
CONTRACT = "0x94219CCCaAD2af43121083e3DDaFb326d2f42cBF"
COVALENT_API = f"https://api.covalenthq.com/v1/{CHAIN_ID}/tokens/{CONTRACT}/token_holders/"
COVALENT_KEY = os.getenv("COVALENT_KEY")
wallets = []
wallet_to_user_id = {}
user_whale_role = {}
tx_count = {}
user_to_wallet_mapping = {}
user_xp = {}

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    intents=intents)

async def assign_role(member, role_name):
    role = nextcord.utils.get(member.guild.roles, name=role_name)
    if role:
        await member.add_roles(role)

def add_wallet(address, user_id):
    wallets.append(address)
    wallet_to_user_id[address] = user_id

@bot.command(name="register")
async def register(ctx, *args):
    wallet_addy = args[0]
    user_id = ctx.author.id
    user_to_wallet_mapping[user_id] = wallet_addy
    # this particular wallet address has to be now tracked
    add_wallet(wallet_addy, user_id)

    await ctx.send(f"<@{ctx.author.id}> has registered {wallet_addy}")

@bot.command(name="xp")
async def xp(ctx):
    user_id = ctx.author.id
    try:
        user_xp[user_id]
    except KeyError:
        user_xp[user_id] = 0
    await ctx.send(f"<@{ctx.author.id}> has {user_xp[user_id]} XP!")

@bot.command(name="unregister")
async def unregister(ctx):
    try:
        del user_to_wallet_mapping[ctx.author.id]
    except KeyError:
        pass
    await ctx.send(f'<@{ctx.author.id}> has unregistered :(')

def add_xp(user_id, amt):
    try:
        user_xp[user_id]+= amt
    except:
        user_xp[user_id] = amt
    
async def handle_event(event, user_id):
    guild = bot.get_guild(GUILD_ID)
    member = guild.get_member(int(user_id))
    channel = bot.get_channel(TARGET_CHANNEL_ID)
    
    if event == "FIRST_TX":
        await assign_role(member, "Rookie Trader")
        add_xp(user_id, 20)
        await channel.send(f"<@{user_id}> gained 20XP + Rookie Trader role for completing your 1st transaction!")

    elif event == "TEN_TX":
        await assign_role(member, "Silver Trader")
        add_xp(user_id, 50)
        await channel.send(f"<@{user_id}> gained 50XP + Silver Trader role for completing 10 transactions!")

    elif event == "FIFTY_TX":
        await assign_role(member, "Gold Trader")
        add_xp(user_id, 500)
        await channel.send(f"<@{user_id}> gained 500XP + Gold Trader role for completing 50 transactions!")
    elif event == "GOLD_WHALE":
        await assign_role(member, "Gold WHALE")
        add_xp(user_id, 200)
        await channel.send(f"<@{user_id}> just became a **GOLD Whale** 🐋")
    elif event == "DIAMOND_WHALE":
        await assign_role(member, "Diamond WHALE")
        add_xp(user_id, 500)
        await channel.send(f"<@{user_id}> just became a **DIAMOND Whale** 🐋")
    elif event == "PLATINUM_WHALE":
        await assign_role(member, "Platinum WHALE")
        add_xp(user_id, 1000)
        await channel.send(f"<@{user_id}> just became a **PLATINUM Whale** 🐋")

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


#   FLASK API SERVER

app = Flask(__name__)

@app.route("/discord-event", methods=["POST"])
def discord_event():
    data = request.get_json()
    event = data.get("event")
    user_id = data.get("user_id")

    bot.loop.create_task(handle_event(event, user_id))
    return jsonify({"ok": True})

def transfer_check(address, user_id):
    count = tx_count[address]
    if count == 50:
        event = "FIFTY_TX"
    elif count == 10:
        event = "TEN_TX"
    elif count == 1:
        event = "FIRST_TX"

    bot.loop.create_task(handle_event(event, user_id))

def holder_check(address, user_id, balance):
    if balance > 10000:
        event = "PLATINUM_WHALE"
    elif balance >= 5000:
        event = "DIAMOND_WHALE"
    elif balance >= 1000:
        event = "GOLD_WHALE"
    bot.loop.create_task(handle_event(event, user_id))

@app.route("/transfer-event", methods=["POST"])
def transfer_event():
    data = request.get_json()
    from_address = data['from_address']
    try:
        wallet_to_user_id[from_address]
    except:
        #address not registered
        return {'message': "wallet not registered"}, 200
    user_id = wallet_to_user_id[from_address]
    try:
        tx_count[from_address] = tx_count[from_address]+1
    except:
        tx_count[from_address] = 1
    
    transfer_check(from_address, user_id)
    return {"message": "success"}, 200

@app.route("/holder-event", methods=["POST"])
def holder_event():
    data = request.get_json()
    from_address = data['from_address']
    to_address = data['to_address']
    if to_address not in wallets:
        return {"message": "wallet not registered"}, 200
    
    user_id = wallet_to_user_id[to_address]
    url = f"{COVALENT_API}?key={COVALENT_KEY}"
    response = requests.get(url, timeout=10)
    data = response.json()
    items = data['data']['items']
    for item in items:
        if item['address'] != to_address:
            continue
        balance = int(item['balance'])/(10**int(item['contract_decimals']))
        try: 
            user_whale_role[to_address]
        except:
            user_whale_role[to_address] = 'none'
        
        holder_check(to_address, user_id, balance)
    
    return {"message": "success"}, 200

@app.route("/", methods=["POST"])
def check():
    return jsonify({"success": True}), 200

def run_flask():
    app.run(host="0.0.0.0", port=BOT_PORT)


threading.Thread(target=run_flask).start()
bot.run(TOKEN) 