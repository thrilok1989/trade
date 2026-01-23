import streamlit as st
import pandas as pd
import requests
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from st_autorefresh import st_autorefresh

###################################
# 📌 PAGE CONFIGURATION
###################################
st.set_page_config(
    page_title="NIFTY S/R Dashboard",
    page_icon="📈",
    layout="wide"
)

###################################
# 📌 AUTO REFRESH
###################################
refresh_count = st_autorefresh(interval=120000, key="refresh_timer", limit=None)

###################################
# 🎨 CUSTOM CSS
###################################
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
        margin: 0.5rem 0;
    }
    .alert-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 5px solid #f59e0b;
        background-color: #fef3c7;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 5px solid #10b981;
        background-color: #d1fae5;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
</style>
""", unsafe_allow_html=True)

###################################
# 🚀 LOAD SECRETS
###################################
st.markdown('<h1 class="main-header">📈 NIFTY Support & Resistance Dashboard</h1>', unsafe_allow_html=True)

# Initialize session state for alerts history
if 'alerts_history' not in st.session_state:
    st.session_state.alerts_history = []

# Configuration in sidebar
with st.sidebar:
    st.title("⚙️ Configuration")
    
    # API Selection
    api_source = st.radio(
        "Data Source:",
        ["Yahoo Finance (Free)", "Mock Data (Demo)", "Alpha Vantage (API Key Required)"],
        index=1
    )
    
    if api_source == "Alpha Vantage (API Key Required)":
        alpha_vantage_key = st.text_input("Alpha Vantage API Key", type="password")
    elif api_source == "Custom API":
        custom_api_url = st.text_input("API Endpoint URL")
        custom_api_key = st.text_input("API Key", type="password")
    
    # Telegram Configuration
    st.subheader("🔔 Telegram Alerts")
    telegram_enabled = st.checkbox("Enable Telegram Alerts", value=False)
    
    if telegram_enabled:
        bot_token = st.text_input("Bot Token", type="password")
        chat_id = st.text_input("Chat ID")
    else:
        bot_token = ""
        chat_id = ""
    
    # Trading Parameters
    st.subheader("📊 Trading Parameters")
    nifty_id = st.number_input("NIFTY Symbol", value=26000, help="Use 26000 for NIFTY 50")
    
    timeframes = st.multiselect(
        "Timeframes",
        ["5m", "15m", "30m", "60m", "1d", "1wk"],
        default=["15m", "60m", "1d"]
    )
    
    threshold = st.slider("Alert Threshold (%)", 0.1, 2.0, 0.5, 0.1)
    
    # Statistics
    st.subheader("📈 Stats")
    st.metric("Refresh Count", refresh_count)
    st.metric("Current Time", datetime.now().strftime("%H:%M:%S"))
    
    if st.button("🔄 Manual Refresh"):
        st.rerun()

###################################
# 🔍 DATA FETCHING FUNCTIONS
###################################
def fetch_yahoo_data(symbol="^NSEI", interval="1d", period="1mo"):
    """Fetch data from Yahoo Finance (free API)"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {
            "interval": interval,
            "range": period,
            "includePrePost": "false"
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if "chart" in data and "result" in data["chart"]:
            result = data["chart"]["result"][0]
            timestamps = result["timestamp"]
            quotes = result["indicators"]["quote"][0]
            
            df = pd.DataFrame({
                "timestamp": pd.to_datetime(timestamps, unit='s'),
                "open": quotes["open"],
                "high": quotes["high"],
                "low": quotes["low"],
                "close": quotes["close"],
                "volume": quotes["volume"]
            })
            
            # Remove NaN values
            df = df.dropna()
            return df
        
        return generate_mock_data(interval)
        
    except Exception as e:
        st.warning(f"Yahoo API error: {e}. Using mock data.")
        return generate_mock_data(interval)

def fetch_alpha_vantage(symbol="NIFTY", interval="60min", apikey="demo"):
    """Fetch data from Alpha Vantage"""
    try:
        function = "TIME_SERIES_INTRADAY" if interval != "1d" else "TIME_SERIES_DAILY"
        
        url = f"https://www.alphavantage.co/query"
        params = {
            "function": function,
            "symbol": "NSE:NIFTY",
            "interval": interval.replace("m", "min") if "m" in interval else "daily",
            "apikey": apikey,
            "outputsize": "compact"
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        # Parse Alpha Vantage response
        if "Time Series" in data:
            time_key = list(data["Time Series"].keys())[0]
            df = pd.DataFrame.from_dict(data["Time Series"], orient='index')
            df.index = pd.to_datetime(df.index)
            df.columns = ["open", "high", "low", "close", "volume"]
            df = df.astype(float)
            df = df.sort_index()
            
            # Reset index to have timestamp column
            df = df.reset_index().rename(columns={"index": "timestamp"})
            return df
        
        return generate_mock_data(interval)
        
    except Exception as e:
        st.warning(f"Alpha Vantage error: {e}. Using mock data.")
        return generate_mock_data(interval)

def generate_mock_data(timeframe):
    """Generate realistic mock data for demonstration"""
    np.random.seed(42)
    
    # Determine number of periods based on timeframe
    periods_map = {
        "5m": 288,   # 24 hours in 5-min intervals
        "15m": 96,   # 24 hours in 15-min intervals
        "30m": 48,   # 24 hours in 30-min intervals
        "60m": 24,   # 24 hours
        "1d": 30,    # 30 days
        "1wk": 12,   # 12 weeks
    }
    
    n_periods = periods_map.get(timeframe, 100)
    base_price = 22000
    
    # Generate timestamps
    if "m" in timeframe:
        freq = timeframe.replace("m", "T")
        dates = pd.date_range(end=datetime.now(), periods=n_periods, freq=freq)
    else:
        freq = timeframe.replace("1", "D").replace("wk", "W")
        dates = pd.date_range(end=datetime.now(), periods=n_periods, freq=freq)
    
    # Generate realistic price movement
    returns = np.random.normal(0, 0.005, n_periods)
    prices = base_price * np.exp(np.cumsum(returns))
    
    # Generate OHLC with some randomness
    df = pd.DataFrame({
        "timestamp": dates,
        "open": prices * (1 + np.random.normal(0, 0.001, n_periods)),
        "high": prices * (1 + np.abs(np.random.normal(0.002, 0.002, n_periods))),
        "low": prices * (1 - np.abs(np.random.normal(0.002, 0.002, n_periods))),
        "close": prices,
        "volume": np.random.randint(1000, 100000, n_periods)
    })
    
    # Ensure high > low and high > close, low < close
    df["high"] = df[["open", "close", "high"]].max(axis=1) * 1.001
    df["low"] = df[["open", "close", "low"]].min(axis=1) * 0.999
    
    return df

def get_ohlc_data(timeframe, source="mock"):
    """Main function to get OHLC data from selected source"""
    if source == "Yahoo Finance (Free)":
        interval_map = {
            "5m": "5m", "15m": "15m", "30m": "30m",
            "60m": "60m", "1d": "1d", "1wk": "1wk"
        }
        period_map = {
            "5m": "1d", "15m": "5d", "30m": "5d",
            "60m": "1mo", "1d": "3mo", "1wk": "1y"
        }
        return fetch_yahoo_data("^NSEI", interval_map.get(timeframe, "1d"), period_map.get(timeframe, "1mo"))
    
    elif source == "Alpha Vantage (API Key Required)":
        if 'alpha_vantage_key' in locals() and alpha_vantage_key:
            return fetch_alpha_vantage("NIFTY", timeframe, alpha_vantage_key)
        else:
            st.warning("Please enter Alpha Vantage API Key")
            return generate_mock_data(timeframe)
    
    else:  # Mock Data
        return generate_mock_data(timeframe)

###################################
# 📊 S/R CALCULATION FUNCTIONS
###################################
def calculate_pivot_points(df):
    """Calculate standard pivot points"""
    if df.empty or len(df) < 2:
        return {}
    
    high = df["high"].max()
    low = df["low"].min()
    close = df["close"].iloc[-1]
    
    pp = (high + low + close) / 3
    r1 = (2 * pp) - low
    s1 = (2 * pp) - high
    r2 = pp + (high - low)
    s2 = pp - (high - low)
    r3 = high + 2 * (pp - low)
    s3 = low - 2 * (high - pp)
    
    return {
        "Pivot": pp,
        "S1": s1, "S2": s2, "S3": s3,
        "R1": r1, "R2": r2, "R3": r3
    }

def calculate_fibonacci_levels(df):
    """Calculate Fibonacci retracement levels"""
    if df.empty or len(df) < 2:
        return {}
    
    high = df["high"].max()
    low = df["low"].min()
    diff = high - low
    
    return {
        "0% (High)": high,
        "23.6%": high - 0.236 * diff,
        "38.2%": high - 0.382 * diff,
        "50%": high - 0.5 * diff,
        "61.8%": high - 0.618 * diff,
        "100% (Low)": low
    }

###################################
# 🔔 ALERT FUNCTIONS
###################################
def send_telegram_message(bot_token, chat_id, message):
    """Send message to Telegram"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code == 200
    except:
        return False

def check_alerts(current_price, sr_levels, threshold_percent):
    """Check if current price is near any S/R levels"""
    alerts = []
    
    for tf_name, levels in sr_levels.items():
        for level_name, level_value in levels.items():
            if isinstance(level_value, (int, float)):
                distance_pct = abs(current_price - level_value) / current_price * 100
                if distance_pct <= threshold_percent:
                    alerts.append({
                        "timeframe": tf_name,
                        "level": level_name,
                        "value": level_value,
                        "current_price": current_price,
                        "distance_pct": distance_pct,
                        "direction": "ABOVE" if current_price > level_value else "BELOW"
                    })
    
    return alerts

###################################
# 📈 CHART FUNCTIONS
###################################
def create_price_chart(df, sr_levels=None, timeframe="1d"):
    """Create interactive price chart"""
    fig = go.Figure()
    
    # Add candlestick
    fig.add_trace(go.Candlestick(
        x=df['timestamp'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Price'
    ))
    
    # Add S/R levels if provided
    if sr_levels:
        colors = {
            'S1': '#ef4444', 'S2': '#dc2626', 'S3': '#b91c1c',
            'R1': '#10b981', 'R2': '#059669', 'R3': '#047857',
            'Pivot': '#6b7280'
        }
        
        for level_name, level_value in sr_levels.items():
            if level_name in colors:
                fig.add_hline(
                    y=level_value,
                    line_dash="dash",
                    line_color=colors[level_name],
                    annotation_text=level_name,
                    annotation_position="right",
                    opacity=0.6
                )
    
    # Update layout
    fig.update_layout(
        title=f"NIFTY Price Chart ({timeframe})",
        yaxis_title="Price",
        xaxis_title="Time",
        template="plotly_white",
        height=500,
        xaxis_rangeslider_visible=False,
        showlegend=True
    )
    
    return fig

###################################
# 🎯 MAIN DASHBOARD
###################################
# Create tabs
tab1, tab2, tab3 = st.tabs(["📊 S/R Dashboard", "📈 Price Charts", "⚙️ Settings & Info"])

with tab1:
    # Fetch and calculate S/R levels
    sr_data = {}
    current_price = 22150.75  # Mock current price
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, tf in enumerate(timeframes):
        progress = (idx + 1) / len(timeframes)
        progress_bar.progress(progress)
        status_text.text(f"Fetching {tf} data...")
        
        # Get data
        df = get_ohlc_data(tf, api_source)
        
        if not df.empty:
            # Calculate both pivot and fibonacci levels
            pivot_levels = calculate_pivot_points(df)
            fib_levels = calculate_fibonacci_levels(df)
            
            sr_data[tf] = {
                **pivot_levels,
                **{f"F_{k}": v for k, v in fib_levels.items()}
            }
    
    progress_bar.empty()
    status_text.empty()
    
    # Display S/R Levels
    if sr_data:
        # Convert to DataFrame for display
        display_data = {}
        for tf, levels in sr_data.items():
            # Filter to show only key levels for cleaner display
            key_levels = {}
            for k, v in levels.items():
                if k in ["Pivot", "S1", "S2", "S3", "R1", "R2", "R3"] or "50%" in str(k):
                    key_levels[k] = v
            display_data[tf] = key_levels
        
        df_sr = pd.DataFrame(display_data).T
        
        # Format and style
        st.subheader("Support & Resistance Levels")
        
        def color_level(val):
            if isinstance(val, (int, float)):
                if 'S' in col:
                    return 'color: #dc2626; font-weight: bold'
                elif 'R' in col:
                    return 'color: #059669; font-weight: bold'
                elif 'Pivot' in col:
                    return 'color: #6b7280; font-weight: bold'
                elif '%' in col:
                    return 'color: #7c3aed; font-weight: bold'
            return ''
        
        styled_df = df_sr.style.format("{:.2f}").applymap(
            color_level,
            subset=pd.IndexSlice[:, df_sr.columns]
        )
        
        st.dataframe(styled_df, use_container_width=True)
        
        # Current Price and Alerts
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                "📍 Current NIFTY Price",
                f"₹{current_price:,.2f}",
                delta="+125.50 (+0.57%)"
            )
            st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            # Check for alerts
            alerts = check_alerts(current_price, sr_data, threshold)
            
            if alerts:
                st.markdown('<div class="alert-box">', unsafe_allow_html=True)
                st.warning(f"⚠️ {len(alerts)} Alert(s) Triggered!")
                
                for alert in alerts[:3]:  # Show first 3 alerts
                    st.write(f"**{alert['timeframe']} {alert['level']}**")
                    st.write(f"Level: ₹{alert['value']:.2f}")
                    st.write(f"Price is {alert['direction']} by {alert['distance_pct']:.2f}%")
                
                if telegram_enabled and bot_token and chat_id:
                    if st.button("📨 Send Telegram Alert", type="primary"):
                        alert_msg = f"🚨 NIFTY Alert!\nPrice: ₹{current_price:.2f}\n"
                        alert_msg += f"Near: {alerts[0]['timeframe']} {alerts[0]['level']}\n"
                        alert_msg += f"Level: ₹{alerts[0]['value']:.2f}"
                        
                        if send_telegram_message(bot_token, chat_id, alert_msg):
                            st.success("Alert sent!")
                            # Log alert
                            st.session_state.alerts_history.append({
                                "time": datetime.now().strftime("%H:%M:%S"),
                                "message": alert_msg
                            })
                        else:
                            st.error("Failed to send alert")
                
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.success("✅ No alerts triggered")
                st.caption(f"Threshold: {threshold}%")
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Download button
        csv = df_sr.to_csv()
        st.download_button(
            label="📥 Download S/R Levels (CSV)",
            data=csv,
            file_name=f"nifty_sr_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
    
    else:
        st.warning("No data available. Please check your settings.")

with tab2:
    st.subheader("Interactive Price Charts")
    
    # Chart timeframe selector
    chart_tf = st.selectbox("Select timeframe for chart:", timeframes, index=0)
    
    # Get data for chart
    chart_data = get_ohlc_data(chart_tf, api_source)
    
    if not chart_data.empty:
        # Calculate S/R for this timeframe
        pivot_levels = calculate_pivot_points(chart_data)
        
        # Create chart
        fig = create_price_chart(chart_data, pivot_levels, chart_tf)
        st.plotly_chart(fig, use_container_width=True)
        
        # Chart statistics
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        with col_stats1:
            st.metric("Open", f"₹{chart_data['open'].iloc[-1]:,.2f}")
        with col_stats2:
            st.metric("High", f"₹{chart_data['high'].max():,.2f}")
        with col_stats3:
            st.metric("Low", f"₹{chart_data['low'].min():,.2f}")
        
        # Raw data viewer
        with st.expander("View Raw Data"):
            st.dataframe(chart_data.tail(20))
    
    else:
        st.info("No chart data available")

with tab3:
    st.subheader("Application Information")
    
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.markdown("""
        ### 📋 How to Use
        
        1. **Configure Data Source** in sidebar
        2. **Select Timeframes** for S/R calculation
        3. **Set Alert Threshold** for notifications
        4. **Enable Telegram** for real-time alerts
        5. **Monitor** S/R levels and price action
        
        ### 🔔 Alert System
        
        Alerts trigger when price approaches:
        - Support/Resistance levels
        - Pivot points
        - Fibonacci levels
        
        Threshold: Price within X% of level
        """)
    
    with col_info2:
        st.markdown("""
        ### 📊 Data Sources
        
        **1. Yahoo Finance (Free)**
        - Real NIFTY data
        - No API key required
        - Limited historical data
        
        **2. Alpha Vantage**
        - Real-time data
        - API key required (free tier available)
        - More comprehensive data
        
        **3. Mock Data**
        - For demonstration
        - Realistic price patterns
        - No API required
        """)
    
    # Alert History
    st.subheader("📜 Alert History")
    if st.session_state.alerts_history:
        for alert in reversed(st.session_state.alerts_history[-10:]):
            st.caption(f"🕒 {alert['time']}: {alert['message']}")
        
        if st.button("Clear History"):
            st.session_state.alerts_history = []
            st.rerun()
    else:
        st.info("No alerts sent yet")
    
    # System Info
    st.subheader("🖥️ System Information")
    col_sys1, col_sys2 = st.columns(2)
    
    with col_sys1:
        st.metric("Python Version", "3.9+")
        st.metric("Streamlit Version", st.__version__)
    
    with col_sys2:
        st.metric("Last Refresh", datetime.now().strftime("%H:%M:%S"))
        st.metric("Refresh Count", refresh_count)

###################################
# 📱 FOOTER
###################################
st.markdown("---")
st.caption(f"""
📈 NIFTY Support & Resistance Dashboard • Version 2.0 • 
Auto-refresh every 2 minutes • Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
""")
st.caption("⚠️ This is for educational purposes only. Trading involves risk.")
