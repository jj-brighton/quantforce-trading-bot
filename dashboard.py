import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="QuantForce Trading Dashboard", layout="wide")

st.title("\U0001F4B8 QuantForce Trading Bot Dashboard")

# Load portfolio and trades
portfolio_file = 'portfolio.json'
trades_file = 'trades.json'

if os.path.exists(portfolio_file):
    portfolio = pd.read_json(portfolio_file)
else:
    portfolio = pd.DataFrame({"cash": [1250], "positions": [{}]})

if os.path.exists(trades_file):
    trades = pd.read_json(trades_file)
else:
    trades = pd.DataFrame(columns=["time", "symbol", "side", "qty", "price"])

# Sidebar
st.sidebar.header("Portfolio Overview")

cash = portfolio.get("cash", [1250])[0]
positions = portfolio.get("positions", [{}])[0]

st.sidebar.metric("Cash Balance ($)", f"{cash:.2f}")

# Positions
st.header("\U0001F4C8 Open Positions")

if positions:
    positions_df = pd.DataFrame.from_dict(positions, orient='index')
    positions_df.index.name = 'Symbol'
    st.dataframe(positions_df)
else:
    st.info("No open positions.")

# Trades
st.header("\U0001F4DD Trade History")

if not trades.empty:
    st.dataframe(trades)
else:
    st.info("No trades yet.")

# Future: add charts, performance tracking etc.