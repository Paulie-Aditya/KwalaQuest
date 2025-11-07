# KwalaQuest

Best Gaming DApp Automation

## Project Overview

KwalaQuest is a Discord-integrated gamification system for on-chain activity. It connects users' wallet activity (tracked via webhooks and the Covalent API) with Discord rewards: XP, level roles, and achievement roles (Trader/Whale tiers). It runs a Nextcord (Discord) bot and a small Flask API in the same process so webhooks can push events to the bot.

Key features:

- Register a wallet to a Discord user via `!register <wallet>`.
- Award XP for on-chain events and track transaction counts.
- Automatic role assignment for milestones (First Tx, 10 Tx, 50 Tx) and whale tiers (Gold/Diamond/Platinum) based on token balance.
- Level system: every 100 XP equals 1 level. Levels 1–10 are supported and map to Discord roles named `Level 1` through `Level 10`.
- `!xp` command shows XP, level, and XP to next level in an embed.
- `!help` command displays milestones and available commands in a nicely formatted embed.

Files of interest:

- `app.py` — main bot + Flask server implementation (commands, web endpoints, XP/leveling, role assignments).
- `requirements.txt` — Python dependencies (nextcord, flask, requests, python-dotenv, gunicorn).
- `.env` — local environment variables (BOT_TOKEN, COVALENT_KEY, BOT_PORT). Do not commit real secrets to public repos.

## Chosen Track

Best Gaming DApp Automation

This project is designed to be used by gaming-focused DApps seeking to gamify players' on-chain activity by automating role rewards, XP, and leaderboards inside Discord.

## Team

- Paulie-Aditya — GitHub: https://github.com/Paulie-Aditya

## Setup (local / development)

1. Create a Python virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Create a `.env` file in the project root (example keys):

```
BOT_TOKEN=<your-discord-bot-token>
COVALENT_KEY=<your-covalent-api-key>
BOT_PORT=5001
```

3. Create the expected Discord roles in your server:

- `Rookie Trader`, `Silver Trader`, `Gold Trader`
- `Gold WHALE`, `Diamond WHALE`, `Platinum WHALE`
- `Level 1` through `Level 10`

The bot expects these exact role names to exist; it will add and remove them automatically.

4. Run the app locally:

```powershell
python app.py
```

This starts the Flask webhook server and the Nextcord bot.

## Endpoints (webhooks)

- `POST /transfer-event` — expects JSON with `from_address` (the bot checks if the wallet is registered) and will increment tx count and possibly trigger a transfer milestone.
- `POST /holder-event` — expects JSON with `from_address` and `to_address`; queries Covalent to find the token balance for the receiving address and may award Whale roles.

## Commands (Discord)

- `!register <wallet>` — Link your wallet to your Discord account.
- `!unregister` — Remove the linked wallet.
- `!xp` — Show current XP, level, and XP to next level (embed).
- `!help` — Show milestones and commands in an embed.

## Future Scope

- Add a `!leaderboard` command to show top XP users.
- Add persistent storage (database) for XP, mappings, and tx counts (currently in-memory).
- Add unit tests and CI workflow.
- Add a small setup script or Discord role creation helper to automate role creation in a server.
