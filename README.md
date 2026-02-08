🤖 Trading Signal Listener - Setup Guide
Automated trading bot that listens to Premium Trading Signals from Telegram and executes trades on Bybit.

📋 Table of Contents

Requirements
Installation
Configuration
Trading Modes
Running the Bot
Running with PM2 (Recommended)
Troubleshooting
Support

🔧 Requirements
System Requirements:

Ubuntu 20.04+ or Debian 10+ (Recommended)
Python 3.10 or higher
VPS with at least 1GB RAM
Stable internet connection

Accounts Needed:

Patreon Subscription - Active membership to Premium Trading Signals
Telegram Account - Personal Telegram account
Bybit Account - Trading account (create at bybit.com)
Telegram API Credentials - From my.telegram.org

📦 Installation
Step 1: Update System
bashsudo apt update && sudo apt upgrade -y
Step 2: Install Python 3.10+
bash# Check Python version
python3 --version

# If Python < 3.10, install:
sudo apt install python3.10 python3.10-venv python3-pip -y

Step 3: Clone Repository
bash# Navigate to home directory
cd ~

# Clone the repository
git clone https://github.com/PremiumTradingSignals/listen_signals.git

# Enter directory
cd listen_signals

Step 4: Create Virtual Environment
bash# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Your prompt should now show (venv)
Step 5: Install Dependencies
bashpip install --upgrade pip
pip install telethon pybit python-dotenv

⚙️ Configuration
Step 1: Get Telegram API Credentials

Go to: https://my.telegram.org/auth
Login with your phone number
Click "API development tools"
Fill in the form:

App title: Trading Listener
Short name: tradinglistener
Platform: Desktop
Description: (optional)


Click "Create application"
Copy your api_id and api_hash

⚠️ Important: Keep these credentials secure!

Step 2: Get Bybit API Keys

Login to Bybit
Go to: Account & Security → API Management
Click "Create New Key"
Settings:

Type: System-generated API Keys
Permissions: ✅ Contract Trade, ✅ Spot Trade
IP Restriction: Add your VPS IP (recommended)


Copy your API Key and API Secret

⚠️ Never share your API keys!

Step 3: Create .env File
bash# In the trading-listener directory
nano .env
Copy and paste this template:

# ============ TELEGRAM CONFIG ============
# Get these from https://my.telegram.org
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890

# Premium Signals Channel ID (provided by admin)
TELEGRAM_CHANNEL_ID=-1001234567890

# ============ BYBIT CONFIG ============
# Your Bybit API credentials
BYBIT_API_KEY=your_api_key_here
BYBIT_API_SECRET=your_api_secret_here

# Set to false for real trading, true for testing
TESTNET=false

# ============ TRADING MODE ============
# Options: MIRROR, FIXED, ALL_IN
TRADING_MODE=MIRROR

# ============ FIXED MODE SETTINGS ============
# How much USDT to spend when buying (BUY signals)
FIXED_AMOUNT_USDT=100

# How much ETH to sell when selling (SELL signals)
FIXED_AMOUNT_ETH=0.04

# ============ ALL_IN MODE SETTINGS ============
# Percentage of balance to use (0.95 = 95%)
ALL_IN_PERCENTAGE=0.95

Save and exit:

Press Ctrl + O (save)
Press Enter (confirm)
Press Ctrl + X (exit)


🎮 Trading Modes
Choose the mode that fits your strategy:
Mode 1: MIRROR (Default)
Copies the exact quantity from signals.

TRADING_MODE=MIRROR
```

**Example:**
```
Signal: BUY 0.05 ETH
Your bot: BUY 0.05 ETH


Best for: Following the exact strategy

Mode 2: FIXED
Trades fixed amounts you set.

TRADING_MODE=FIXED
FIXED_AMOUNT_USDT=100
FIXED_AMOUNT_ETH=0.04
```

**Example:**
```
Signal: BUY 0.05 ETH
Your bot: BUY $100 worth of ETH (~0.04 ETH at $2,500)

Signal: SELL 0.05 ETH
Your bot: SELL 0.04 ETH

Best for: Conservative trading with set risk

Mode 3: ALL_IN
Uses percentage of your total balance.

TRADING_MODE=ALL_IN
ALL_IN_PERCENTAGE=0.95
```

**Example:**
```
Your balance: $1,000 USDT
Signal: BUY ETH
Your bot: BUY $950 worth of ETH (95%)

Your balance: 1.0 ETH
Signal: SELL ETH
Your bot: SELL 0.95 ETH (95%)

Best for: Aggressive trading, maximizing returns

🚀 Running the Bot
First Time Setup

# Activate virtual environment (if not already)
source venv/bin/activate

# Run the bot
python listen_signals.py
```

**First run will ask for:**
```
Please enter your phone (or bot token): +1234567890
```
Enter your phone number with country code.
```
Please enter the code you received: 12345
```
Check Telegram for the code and enter it.

✅ **Done!** The bot is now running.

---

### **You should see:**
```
══════════════════════════════════════════════════════
🤖 TRADING SIGNAL LISTENER
══════════════════════════════════════════════════════
   Trading Mode: MIRROR
   Channel: -1001234567890
   Bybit: MAINNET
══════════════════════════════════════════════════════

✅ Logged in as: John (@johndoe)
🎧 Listening for signals...

🔄 Running with PM2 (Recommended)
PM2 keeps your bot running 24/7, even after system reboot.
Step 1: Install Node.js and PM2
bash# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PM2
sudo npm install -g pm2

Step 2: Create Startup Script
bash# Create start script
nano start.sh
Paste this:

bash#!/bin/bash
cd /home/YOUR_USERNAME/trading-listener
source venv/bin/activate
python listen_signals.py
Replace YOUR_USERNAME with your actual username (find it with whoami).
Make it executable:
bashchmod +x start.sh

Step 3: Start with PM2
bashpm2 start start.sh --name trading-listener
Step 4: Enable Auto-Start on Reboot

# Save current PM2 processes
pm2 save

# Generate startup script
pm2 startup

# Copy and run the command PM2 gives you
# It will look like:
# sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u yourusername --hp /home/yourusername

📊 PM2 Commands

# View status
pm2 status

# View logs (real-time)
pm2 logs trading-listener

# View last 100 lines
pm2 logs trading-listener --lines 100

# Restart bot
pm2 restart trading-listener

# Stop bot
pm2 stop trading-listener

# Delete from PM2
pm2 delete trading-listener

# Monitor (CPU/RAM usage)
pm2 monit

🐛 Troubleshooting
Problem: "ModuleNotFoundError: No module named 'telethon'"
Solution:
bashsource venv/bin/activate
pip install telethon pybit python-dotenv

Problem: "Can't connect to Telegram"
Solution:

Check your TELEGRAM_API_ID and TELEGRAM_API_HASH in .env
Make sure you're using correct phone number format: +1234567890
Delete trading_session.session file and try again:

bash   rm trading_session.session
   python listen_signals.py

Problem: "Can't access channel"
Solution:

Make sure you joined the Premium Signals channel via invite link
Check TELEGRAM_CHANNEL_ID in .env is correct
Verify you're in the channel on Telegram app

Problem: "Bybit API error"
Solution:

Check your BYBIT_API_KEY and BYBIT_API_SECRET in .env
Verify API permissions include "Contract Trade" and "Spot Trade"
If using IP restriction, add your VPS IP to Bybit API settings

Problem: Bot keeps restarting
Solution:
bash# Check logs
pm2 logs trading-listener --lines 50

# Look for error messages and fix them
# Common issues: wrong credentials, network problems

Problem: "No signals received"
Solution:

Verify you're in the correct Telegram channel
Check if there are new messages in the channel (on Telegram app)
Restart the bot:

pm2 restart trading-listener
```

---

## 📁 File Structure
```
trading-listener/
├── listen_signals.py          # Main bot script
├── .env                        # Your configuration (DO NOT SHARE!)
├── start.sh                    # PM2 startup script
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── venv/                       # Virtual environment
└── trading_session.session     # Telegram session (created on first run)

🔒 Security Best Practices

✅ Never share your .env file
✅ Use IP restriction on Bybit API
✅ Enable 2FA on Bybit account
✅ Keep VPS system updated

bash   sudo apt update && sudo apt upgrade -y

✅ Use firewall

bash   sudo ufw enable
   sudo ufw allow ssh

📞 Support
Need Help?

Check logs first:

bash   pm2 logs trading-listener

Common issues: See Troubleshooting section
Still stuck?

💬 Contact via Patreon DM

⚠️ Disclaimer
IMPORTANT: Trading cryptocurrencies involves substantial risk of loss. This bot is provided as-is without any warranties. Past performance is not indicative of future results. Only trade with money you can afford to lose. You are solely responsible for your trading decisions and results.
By using this software, you acknowledge that:

You understand the risks of cryptocurrency trading
You have tested the bot on testnet before live trading
You will not hold the developer responsible for any losses
You are using this software at your own risk

📜 License
© 2026 Premium Trading Signals. All rights reserved.
This software is provided exclusively to paying Patreon members. Redistribution or sharing is prohibited.

🚀 Happy Trading!
For updates and announcements, check the Telegram channel or Patreon posts.



