import time
import os
import logging
import alpaca_trade_api as tradeapi
import pandas as pd
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
BASE_URL = "https://paper-api.alpaca.markets"
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Connect to Alpaca
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

# Settings
WATCHLIST = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "META", "AMD", "NFLX", "GOOGL", "JPM"]
TIMEFRAME = "5Min"
SHORT_WINDOW = 5
LONG_WINDOW = 20
RISK_PER_TRADE = 25  # USD risk per trade
STARTING_BALANCE = 1250  # USD
SLEEP_INTERVAL = 300  # 5 minutes
STOP_LOSS_PERCENT = 0.05  # 5%

# Internal portfolio tracker
portfolio = {
    "cash": STARTING_BALANCE,
    "positions": {}
}

# Load saved portfolio if exists
if os.path.exists('portfolio.json'):
    portfolio = pd.read_json('portfolio.json').to_dict()

# Send Telegram message
def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, data=payload)
    except Exception as e:
        logging.error(f"Error sending Telegram message: {e}")

# Fetch stock data
def fetch_data(symbol):
    barset = api.get_barset(symbol, TIMEFRAME, limit=LONG_WINDOW + 5)
    bars = barset[symbol]
    data = pd.DataFrame({
        'time': [bar.t for bar in bars],
        'open': [bar.o for bar in bars],
        'high': [bar.h for bar in bars],
        'low': [bar.l for bar in bars],
        'close': [bar.c for bar in bars],
        'volume': [bar.v for bar in bars]
    })
    return data

# Calculate signals
def calculate_signals(data):
    data['SMA_short'] = data['close'].rolling(window=SHORT_WINDOW).mean()
    data['SMA_long'] = data['close'].rolling(window=LONG_WINDOW).mean()
    if data['SMA_short'].iloc[-2] < data['SMA_long'].iloc[-2] and data['SMA_short'].iloc[-1] > data['SMA_long'].iloc[-1]:
        return "buy"
    elif data['SMA_short'].iloc[-2] > data['SMA_long'].iloc[-2] and data['SMA_short'].iloc[-1] < data['SMA_long'].iloc[-1]:
        return "sell"
    return None

# Place order
def place_order(symbol, side, quantity):
    try:
        logging.info(f"Submitting {side} order for {quantity} shares of {symbol}")
        api.submit_order(
            symbol=symbol,
            qty=quantity,
            side=side,
            type='market',
            time_in_force='gtc'
        )
        send_telegram_message(f"{side.capitalize()} order: {quantity} shares of {symbol}")
    except Exception as e:
        logging.error(f"Error placing order: {e}")

# Manage positions
def manage_positions():
    to_sell = []
    for symbol, position in portfolio["positions"].items():
        try:
            current_price = api.get_last_trade(symbol).price
            if current_price <= position["entry_price"] * (1 - STOP_LOSS_PERCENT):
                logging.info(f"Stop-loss triggered for {symbol}")
                to_sell.append(symbol)
        except Exception as e:
            logging.error(f"Error checking stop-loss for {symbol}: {e}")
    for symbol in to_sell:
        qty = portfolio["positions"][symbol]["quantity"]
        place_order(symbol, "sell", qty)
        portfolio["cash"] += qty * api.get_last_trade(symbol).price
        del portfolio["positions"][symbol]

# Save portfolio
def save_portfolio():
    pd.DataFrame.from_dict(portfolio).to_json('portfolio.json')

# Main loop
def main_loop():
    while True:
        try:
            manage_positions()
            for symbol in WATCHLIST:
                data = fetch_data(symbol)
                signal = calculate_signals(data)
                if signal == "buy" and symbol not in portfolio["positions"]:
                    price = api.get_last_trade(symbol).price
                    quantity = int(RISK_PER_TRADE / price)
                    if quantity >= 1 and portfolio["cash"] >= quantity * price:
                        place_order(symbol, "buy", quantity)
                        portfolio["positions"][symbol] = {"entry_price": price, "quantity": quantity}
                        portfolio["cash"] -= quantity * price
                elif signal == "sell" and symbol in portfolio["positions"]:
                    qty = portfolio["positions"][symbol]["quantity"]
                    place_order(symbol, "sell", qty)
                    portfolio["cash"] += qty * api.get_last_trade(symbol).price
                    del portfolio["positions"][symbol]
            save_portfolio()
            time.sleep(SLEEP_INTERVAL)
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    main_loop()
