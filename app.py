import streamlit as st
import pandas as pd
import requests
from dhanhq import DhanContext, dhanhq
from streamlit_autorefresh import st_autorefresh

###################################
# 🚀 Auto Refresh
###################################
# st_autorefresh returns refresh count,
# it automatically reruns the script
count = st_autorefresh(
    interval=120000,  # 120000 ms = 2 minutes
    limit=None,
    key="auto_refresh"
)

###################################
# ⚡ Load Secrets
###################################
CLIENT_ID = st.secrets["Dhan"]["CLIENT_ID"]
ACCESS_TOKEN = st.secrets["Dhan"]["ACCESS_TOKEN"]
BOT_TOKEN = st.secrets["Telegram"]["BOT_TOKEN"]
CHAT_ID = st.secrets["Telegram"]["CHAT_ID"]

st.title("📈 NIFTY HTF Levels + Telegram Alerts (Auto Refresh every 2 mins)")

###################################
# 👤 Initialize API
###################################
try:
    dhc = DhanContext(CLIENT_ID, ACCESS_TOKEN)
    api = dhanhq(dhc)
except Exception as e:
    st.error(f"API init failed: {e}")
    st.stop()

NIFTY_INST_ID = st.number_input("NIFTY Security ID:", value=13)

###################################
# 📊 Support/Resistance Logic
###################################
def calc_pivots(df):
    H = df["high"].max()
    L = df["low"].min()
    C = df["close"].iloc[-1]
    PP = (H + L + C) / 3
    S1 = (2*PP) - H
    R1 = (2*PP) - L
    S2 = PP - (H - L)
    R2 = PP + (H - L)
    return {"PP": PP, "S1": S1, "R1": R1, "S2": S2, "R2": R2}

def fetch_ohlc(sec_id, interval):
    data = api.fetch_historical_candles(
        security_id=str(sec_id),
        interval=interval
    )
    df = pd.DataFrame(data["candles"])
    df.columns = ["timestamp", "open", "high", "low", "close", "volume"]
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

###################################
# 📋 Display HTF Levels Table
###################################
htf = {}
for tf in ["5m", "15m", "60m"]:
    try:
        df_tf = fetch_ohlc(NIFTY_INST_ID, tf)
        htf[tf] = calc_pivots(df_tf)
    except Exception as e:
        st.error(f"{tf} fetch error: {e}")

if htf:
    df_levels = pd.DataFrame(htf).T
    st.subheader("🧠 HTF Support & Resistance")
    st.dataframe(df_levels.style.format("{:.2f}"))

###################################
# 🔔 Price & Telegram Alerts
###################################
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

try:
    quote = api.ohlc_data(securities={"IDX_I":[NIFTY_INST_ID]})
    price = quote["ticker_data"][0]["last_traded_price"]
    st.write(f"📍 Current NIFTY LTP: {price:.2f}")

    near_msgs = []
    for tf, vals in htf.items():
        for lv_name, lv_val in vals.items():
            if abs(price - lv_val) <= price * 0.003:  # 0.3% threshold
                near_msgs.append(f"{tf} {lv_name} ~ {lv_val:.2f}")

    if near_msgs:
        alert_text = "🔔 Price near HTF S/R:\n" + "\n".join(near_msgs)
        send_telegram(alert_text)
        st.success("📨 Telegram alert sent!")
    else:
        st.info("✔ No levels near current price.")

except Exception as e:
    st.error(f"Quote/alert error: {e}")