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
        xp_points = user_xp[user_id]
    except KeyError:
        xp_points = user_xp[user_id] = 0
    
    current_level = get_level(xp_points)
    next_level_xp = (current_level + 1) * 100
    xp_needed = next_level_xp - xp_points

    embed = nextcord.Embed(title="🎮 XP Status", color=0x00ff00)
    embed.add_field(name="Current XP", value=str(xp_points), inline=True)
    embed.add_field(name="Level", value=str(current_level), inline=True)
    embed.add_field(name="XP to Next Level", value=str(xp_needed), inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name="help")
async def help_command(ctx):
    embed = nextcord.Embed(
        title="🏆 KwalaQuest Milestones",
        description="Complete these milestones to earn roles and XP!",
        color=0x00ff00
    )
    
    # Trading Milestones
    embed.add_field(
        name="📈 Trading Achievements",
        value="• First Transaction: Rookie Trader role + 20 XP\n"
              "• 10 Transactions: Silver Trader role + 50 XP\n"
              "• 50 Transactions: Gold Trader role + 500 XP",
        inline=False
    )
    
    # Whale Status
    embed.add_field(
        name="🐋 Whale Status",
        value="• 1,000+ tokens: Gold WHALE + 200 XP\n"
              "• 5,000+ tokens: Diamond WHALE + 500 XP\n"
              "• 10,000+ tokens: Platinum WHALE + 1,000 XP",
        inline=False
    )
    
    # Level System
    embed.add_field(
        name="⭐ Level System",
        value="• Every 100 XP = 1 Level\n"
              "• Levels 1-10 available\n"
              "• Each level grants a unique role",
        inline=False
    )
    
    # Commands
    embed.add_field(
        name="🤖 Available Commands",
        value="• `!register <wallet>`: Link your wallet\n"
              "• `!unregister`: Unlink your wallet\n"
              "• `!xp`: Check your XP and level\n"
              "• `!help`: Show this help message",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name="unregister")
async def unregister(ctx):
    try:
        del user_to_wallet_mapping[ctx.author.id]
    except KeyError:
        pass
    await ctx.send(f'<@{ctx.author.id}> has unregistered :(')

def get_level(xp):
    return xp // 1000  # Every 1000 XP is one level

async def check_level_up(user_id, guild):
    current_xp = user_xp[user_id]
    current_level = get_level(current_xp)
    
    # Assign level roles
    member = guild.get_member(int(user_id))
    if member:
        # Remove old level roles
        for i in range(1, 11):
            old_role = nextcord.utils.get(guild.roles, name=f"Level {i}")
            if old_role and old_role in member.roles:
                await member.remove_roles(old_role)
        
        # Add new level role if level is between 1-10
        if 1 <= current_level <= 10:
            new_role = nextcord.utils.get(guild.roles, name=f"Level {current_level}")
            if new_role:
                await member.add_roles(new_role)
                channel = bot.get_channel(TARGET_CHANNEL_ID)
                await channel.send(f"🎉 Congratulations <@{user_id}>! You've reached Level {current_level}!")

def add_xp(user_id, amt):
    try:
        old_level = get_level(user_xp[user_id])
        user_xp[user_id] += amt
        new_level = get_level(user_xp[user_id])
        
        if new_level > old_level:
            guild = bot.get_guild(GUILD_ID)
            if guild:
                bot.loop.create_task(check_level_up(user_id, guild))
    except:
        user_xp[user_id] = amt
        guild = bot.get_guild(GUILD_ID)
        if guild:
            bot.loop.create_task(check_level_up(user_id, guild))

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

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run(TOKEN) 