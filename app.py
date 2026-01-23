import streamlit as st
import pandas as pd
import requests
from dhanhq import DhanContext, dhanhq
from st_autorefresh import st_autorefresh

###################################
# 📌 AUTO REFRESH
###################################
# Refresh the script every 120000 ms (2 minutes)
refresh_count = st_autorefresh(interval=120000, key="refresh_timer")

st.title("📈 NIFTY HTF Support & Resistance + Telegram Alerts (2-min Auto Update)")

###################################
# 🚀 LOAD SECRETS
###################################
# Must set these in Streamlit Secrets
CLIENT_ID = st.secrets["Dhan"]["CLIENT_ID"]
ACCESS_TOKEN = st.secrets["Dhan"]["ACCESS_TOKEN"]
BOT_TOKEN = st.secrets["Telegram"]["BOT_TOKEN"]
CHAT_ID = st.secrets["Telegram"]["CHAT_ID"]

###################################
# 🔌 Initialize Dhan API
###################################
try:
    dhc = DhanContext(CLIENT_ID, ACCESS_TOKEN)
    api = dhanhq(dhc)
except Exception as e:
    st.error(f"Failed to init Dhan API: {e}")
    st.stop()

# Enter NIFTY index security ID from your API
NIFTY_ID = st.number_input("NIFTY Security ID (IDX)", value=13)

###################################
# 🔍 HTF S/R Calculation
###################################
def calc_pivots(df):
    """
    Calculate pivot points and support/resistance levels
    """
    high = df["high"].max()
    low = df["low"].min()
    close = df["close"].iloc[-1]
    PP = (high + low + close) / 3
    S1 = (2 * PP) - high
    R1 = (2 * PP) - low
    S2 = PP - (high - low)
    R2 = PP + (high - low)
    return {"PP": PP, "S1": S1, "R1": R1, "S2": S2, "R2": R2}

def fetch_ohlc(sec_id, interval):
    """
    Fetch intraday OHLC from Dhan API
    """
    df = api.fetch_historical_candles(security_id=str(sec_id), interval=interval)
    df = pd.DataFrame(df["candles"])
    df.columns = ["timestamp", "open", "high", "low", "close", "volume"]
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

###################################
# 📊 Display HTF Table
###################################
htf_levels = {}
for timeframe in ["5m", "15m", "60m"]:
    try:
        df_tf = fetch_ohlc(NIFTY_ID, timeframe)
        htf_levels[timeframe] = calc_pivots(df_tf)
    except Exception as e:
        st.error(f"Error fetching {timeframe} data: {e}")

if htf_levels:
    df_table = pd.DataFrame(htf_levels).T
    st.subheader("🧠 HTF Support & Resistance Levels")
    st.dataframe(df_table.style.format("{:.2f}"))

###################################
# 🔔 LIVE PRICE + ALERTS
###################################
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

try:
    quote = api.ohlc_data(securities={"IDX_I":[NIFTY_ID]})
    last_price = quote["ticker_data"][0]["last_traded_price"]
    st.write(f"📍 Current NIFTY Last Traded Price: {last_price:.2f}")

    # Check if price is near any pivot/level
    alerts = []
    for tf, levels in htf_levels.items():
        for lvl_name, lvl_val in levels.items():
            if abs(last_price - lvl_val) <= last_price * 0.003:  # 0.3% threshold
                alerts.append(f"{tf} {lvl_name} ≈ {lvl_val:.2f} (LTP {last_price:.2f})")

    if alerts:
        message = "🔔 *Price Near HTF Support/Resistance:* \n" + "\n".join(alerts)
        send_telegram(message)
        st.success("📨 Telegram alert sent!")
    else:
        st.info("✔ No HTF level near current price.")

except Exception as e:
    st.error(f"Failed to get live price / send alert: {e}")