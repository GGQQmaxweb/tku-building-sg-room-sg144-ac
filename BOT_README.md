# TKU Building SG Room SG144 AC - Discord Bot

This Discord bot allows you to control the Air Conditioner in SG144 using slash commands (`/ac` and `/ping`), leveraging the underlying session login and SCADA control API.

## Features
- **`/ac <temperature>`**: Authenticates and sets the target temperature for SG144.
- **`/ping`**: Checks bot responsiveness.

---

## Setup & Running

### 1. Install Dependencies
Make sure you have Python installed, then install the required packages:
```bash
pip install discord.py requests
```

### 2. Set your Discord Bot Token
Set your bot token in your environment variables:
```bash
export DISCORD_TOKEN="your_discord_bot_token_here"
```

### 3. Run the Bot
```bash
python bot.py
```
