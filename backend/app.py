from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
app = Flask(__name__)

load_dotenv()

# Config
CHAIN_ID = 137  # Polygon mainnet
CONTRACT = "0x94219CCCaAD2af43121083e3DDaFb326d2f42cBF"
COVALENT_API = f"https://api.covalenthq.com/v1/{CHAIN_ID}/tokens/{CONTRACT}/token_holders/"
COVALENT_KEY = os.getenv("COVALENT_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
wallets = []
wallet_to_user_id = {}
user_whale_role = {}

def check_gold_whale_role(address, balance):
    if(user_whale_role[address] == 'gold'):
        return True
    if balance > 1000:
        # assign whale role
        user_id = wallet_to_user_id[address]
        msg = {
            "content": f'<@{user_id}> is now a GOLD Whale!'
        }
        requests.post(
            DISCORD_WEBHOOK, json=msg, timeout=5
        )
        return True
    return False

def check_diamond_whale_role(address, balance):
    if(user_whale_role[address] == 'diamond'):
        return True
    if balance > 1000:
        # assign whale role
        user_id = wallet_to_user_id[address]
        msg = {
            "content": f'<@{user_id}> is now a DIAMOND Whale!'
        }
        requests.post(
            DISCORD_WEBHOOK, json=msg, timeout=5
        )
        return True
    return False

def check_platinum_whale_role(address, balance):
    if(user_whale_role[address] == 'platinum'):
        return True
    if balance > 10000:
        # assign whale role
        user_id = wallet_to_user_id[address]
        msg = {
            "content": f'<@{user_id}> is now a PLATINUM Whale!'
        }
        requests.post(
            DISCORD_WEBHOOK, json=msg, timeout=5
        )
        return True
    return False

@app.route("/add-wallet", methods=["POST"])
def add_wallet():
    data = request.get_json()
    address = data['address']
    user_id = data['user_id']

    wallets.append(address)
    wallet_to_user_id[address] = user_id
    return {"message":"success"}, 200

@app.route("/", methods=["POST"])
def check():
    try:
        url = f"{COVALENT_API}?key={COVALENT_KEY}"
        response = requests.get(url, timeout=10)
        data = response.json()

        if "data" not in data or "items" not in data["data"]:
            return jsonify({"error": "Bad Covalent response", "response": data}), 400
        
        items = data['data']['items']
        holder_count = len(items)
        for item in items:
            address = item['address']
            balance = int(item['balance'])/(10**int(item['contract_decimals']))
            
            if address in wallets :
                try: 
                    user_whale_role[address]
                except:
                    user_whale_role[address] = 'none'

                if check_platinum_whale_role(address, balance):
                    user_whale_role[address] = 'diamond'
                elif check_diamond_whale_role(address, balance):
                    user_whale_role[address] = 'diamond'
                elif check_gold_whale_role(address, balance):
                    user_whale_role[address] = 'gold'
                else:
                    user_whale_role[address] = 'diamond'

        return jsonify({"success": True})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)