# QuantForce Trading Bot

This is a fully working trading bot that:
- Connects to Alpaca Paper Trading
- Trades 10 US stocks based on Moving Average Crossover strategy
- Sends Telegram alerts for every trade
- Displays a live dashboard showing portfolio, trades, and graphs

---

## Setup Instructions

### 1. Requirements
- Python 3.10+
- Alpaca Paper Trading account (for API keys)
- Telegram bot (for alerts)

Install Python libraries:


---

### 2. Files
| File | Purpose |
|:---|:---|
| bot.py | Trading bot engine |
| dashboard.py | Streamlit dashboard |
| requirements.txt | Libraries needed |
| start.sh | Bot start script |
| dashboard_start.sh | Dashboard start script |
| Procfile | Render deployment instructions |
| portfolio.json | Tracks current holdings |
| trades.json | Tracks trade history |

---

### 3. Environment Variables
Set these in Render for both bot and dashboard:

- `API_KEY` → your Alpaca API Key
- `API_SECRET` → your Alpaca API Secret
- `TELEGRAM_TOKEN` → your Telegram Bot token
- `TELEGRAM_CHAT_ID` → your Telegram chat ID

---

### 4. Deployment (Render.com)
- Deploy bot as **Background Worker** → Start Command: `bash start.sh`
- Deploy dashboard as **Web Service** → Start Command: `bash dashboard_start.sh`

---

# Usage

- The bot trades automatically based on moving averages.
- Telegram alerts are sent for every buy/sell/stop-loss.
- The dashboard refreshes live every 60 seconds.
