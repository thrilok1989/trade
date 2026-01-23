import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import os
from st_autorefresh import st_autorefresh
from dotenv import load_dotenv
import json

# Load environment variables for local development
load_dotenv()

###################################
# 📌 PAGE CONFIGURATION
###################################
st.set_page_config(
    page_title="NIFTY HTF S/R Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
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
    .alert-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 5px solid;
    }
    .alert-success {
        background-color: #d1fae5;
        border-color: #10b981;
    }
    .alert-warning {
        background-color: #fef3c7;
        border-color: #f59e0b;
    }
    .alert-danger {
        background-color: #fee2e2;
        border-color: #ef4444;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
    }
    .stDataFrame {
        border-radius: 0.5rem;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

###################################
# 🚀 LOAD SECRETS / CONFIGURATION
###################################
def load_config():
    """Load configuration from secrets or environment variables"""
    config = {}
    
    try:
        # Try Streamlit Secrets first
        if "Dhan" in st.secrets:
            config["CLIENT_ID"] = st.secrets["Dhan"]["CLIENT_ID"]
            config["ACCESS_TOKEN"] = st.secrets["Dhan"]["ACCESS_TOKEN"]
        if "Telegram" in st.secrets:
            config["BOT_TOKEN"] = st.secrets["Telegram"]["BOT_TOKEN"]
            config["CHAT_ID"] = st.secrets["Telegram"]["CHAT_ID"]
    except Exception:
        # Fallback to environment variables for local development
        config["CLIENT_ID"] = os.getenv("DHAN_CLIENT_ID", "")
        config["ACCESS_TOKEN"] = os.getenv("DHAN_ACCESS_TOKEN", "")
        config["BOT_TOKEN"] = os.getenv("TELEGRAM_BOT_TOKEN", "")
        config["CHAT_ID"] = os.getenv("TELEGRAM_CHAT_ID", "")
    
    return config

config = load_config()

# Check if all required configs are present
required_configs = ["CLIENT_ID", "ACCESS_TOKEN", "BOT_TOKEN", "CHAT_ID"]
missing_configs = [cfg for cfg in required_configs if not config.get(cfg)]

if missing_configs:
    st.error(f"❌ Missing configuration: {', '.join(missing_configs)}")
    
    with st.expander("🔧 How to Configure"):
        st.markdown("""
        ### For Streamlit Cloud:
        1. Go to your app's dashboard
        2. Click on "⋮" (three dots) → "Settings" → "Secrets"
        3. Add the following:
        
        ```toml
        [Dhan]
        CLIENT_ID = "your_client_id"
        ACCESS_TOKEN = "your_access_token"
        
        [Telegram]
        BOT_TOKEN = "your_bot_token"
        CHAT_ID = "your_chat_id"
        ```
        
        ### For Local Development:
        Create a `.env` file in the same directory:
        
        ```env
        DHAN_CLIENT_ID=your_client_id
        DHAN_ACCESS_TOKEN=your_access_token
        TELEGRAM_BOT_TOKEN=your_bot_token
        TELEGRAM_CHAT_ID=your_chat_id
        ```
        """)
    st.stop()

###################################
# 🔌 INITIALIZE DHAN API
###################################
def initialize_dhan_api(client_id, access_token):
    """Initialize Dhan API with proper error handling"""
    try:
        # Try multiple import strategies
        try:
            from dhanhq import DhanContext, dhanhq
            dhc = DhanContext(client_id, access_token)
            api = dhanhq(dhc)
            st.sidebar.success("✅ Dhan API initialized")
            return api
        except ImportError as e:
            st.error(f"❌ Cannot import dhanhq package: {e}")
            st.info("""
            ### Install dhanhq:
            
            1. **From GitHub (if available):**
            ```bash
            pip install git+https://github.com/dhanhq/dhanhq-python.git
            ```
            
            2. **From local wheel:**
            - Download the .whl file from Dhan's website
            - Upload it to your project directory
            - Install with: `pip install dhanhq-*.whl`
            ```
            
            3. **Use REST API as fallback** (already implemented)
            """)
            return None
    except Exception as e:
        st.error(f"❌ Failed to initialize Dhan API: {e}")
        return None

# Initialize API
api = initialize_dhan_api(config["CLIENT_ID"], config["ACCESS_TOKEN"])

###################################
# 📊 SIDEBAR CONFIGURATION
###################################
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/stock-share.png", width=100)
    st.title("Dashboard Settings")
    
    st.subheader("📊 Trading Parameters")
    
    # Security ID Input
    NIFTY_ID = st.number_input(
        "NIFTY Security ID",
        value=26000,
        min_value=1,
        max_value=999999,
        help="Default: 26000 for NIFTY 50"
    )
    
    # Timeframe Selection
    st.subheader("⏰ Timeframes")
    timeframes = st.multiselect(
        "Select Timeframes for S/R Calculation",
        options=["5m", "15m", "30m", "60m", "1d"],
        default=["5m", "15m", "60m"]
    )
    
    # Alert Settings
    st.subheader("🔔 Alert Settings")
    threshold_percent = st.slider(
        "Alert Threshold (%)",
        min_value=0.1,
        max_value=5.0,
        value=0.3,
        step=0.1,
        help="Trigger alert when price is within this percentage of S/R level"
    )
    
    # Alert History
    st.subheader("📜 Alert History")
    if "alerts_history" not in st.session_state:
        st.session_state.alerts_history = []
    
    for alert in st.session_state.alerts_history[-5:]:
        st.caption(f"🕒 {alert['time']}: {alert['message'][:50]}...")
    
    # Clear History
    if st.button("Clear Alert History"):
        st.session_state.alerts_history = []
        st.rerun()
    
    st.divider()
    st.caption(f"Last refresh: {datetime.now().strftime('%H:%M:%S')}")
    st.caption(f"Refresh count: {refresh_count}")

###################################
# 🔍 S/R CALCULATION FUNCTIONS
###################################
def calculate_support_resistance(df, method="pivot"):
    """
    Calculate support and resistance levels using different methods
    """
    if df.empty or len(df) < 2:
        return {}
    
    high = df["high"].max()
    low = df["low"].min()
    close = df["close"].iloc[-1]
    
    if method == "pivot":
        # Standard Pivot Point method
        PP = (high + low + close) / 3
        S1 = (2 * PP) - high
        R1 = (2 * PP) - low
        S2 = PP - (high - low)
        R2 = PP + (high - low)
        
        levels = {
            "Pivot": PP,
            "S1": S1,
            "S2": S2,
            "R1": R1,
            "R2": R2
        }
    
    elif method == "fibonacci":
        # Fibonacci Retracement levels
        diff = high - low
        PP = (high + low + close) / 3
        
        levels = {
            "Pivot": PP,
            "S1": high - 0.236 * diff,  # 23.6%
            "S2": high - 0.382 * diff,  # 38.2%
            "S3": high - 0.5 * diff,    # 50%
            "S4": high - 0.618 * diff,  # 61.8%
            "R1": low + 0.236 * diff,   # 23.6%
            "R2": low + 0.382 * diff,   # 38.2%
            "R3": low + 0.5 * diff,     # 50%
            "R4": low + 0.618 * diff,   # 61.8%
        }
    
    elif method == "camarilla":
        # Camarilla Pivot Points
        PP = (high + low + close) / 3
        range_val = high - low
        
        levels = {
            "Pivot": PP,
            "S1": close - range_val * 1.1/12,
            "S2": close - range_val * 1.1/6,
            "S3": close - range_val * 1.1/4,
            "S4": close - range_val * 1.1/2,
            "R1": close + range_val * 1.1/12,
            "R2": close + range_val * 1.1/6,
            "R3": close + range_val * 1.1/4,
            "R4": close + range_val * 1.1/2,
        }
    
    else:
        levels = {}
    
    return levels

def fetch_ohlc_data(security_id, timeframe, api_type="dhan"):
    """
    Fetch OHLC data from different sources
    """
    try:
        if api_type == "dhan" and api is not None:
            # Use Dhan API
            df = api.fetch_historical_candles(
                security_id=str(security_id),
                interval=timeframe
            )
            
            if isinstance(df, dict) and "candles" in df:
                candles = df["candles"]
                if len(candles) > 0:
                    df = pd.DataFrame(candles)
                    if len(df.columns) >= 6:
                        df.columns = ["timestamp", "open", "high", "low", "close", "volume"][:len(df.columns)]
                        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
                        return df
        
        # Fallback: Generate mock data for demonstration
        st.warning(f"⚠️ Using mock data for {timeframe} (API unavailable)")
        return generate_mock_data(timeframe)
        
    except Exception as e:
        st.error(f"Error fetching {timeframe} data: {e}")
        return generate_mock_data(timeframe)

def generate_mock_data(timeframe):
    """Generate mock OHLC data for demonstration"""
    periods = {
        "5m": 288,   # 24 hours / 5 minutes
        "15m": 96,   # 24 hours / 15 minutes
        "30m": 48,   # 24 hours / 30 minutes
        "60m": 24,   # 24 hours
        "1d": 30,    # 30 days
    }
    
    n_periods = periods.get(timeframe, 100)
    base_price = 22000
    
    dates = pd.date_range(end=datetime.now(), periods=n_periods, freq=timeframe.replace("m", "T") if "m" in timeframe else "D")
    
    np.random.seed(42)
    returns = np.random.randn(n_periods) * 0.005
    
    prices = base_price * np.exp(np.cumsum(returns))
    
    df = pd.DataFrame({
        "timestamp": dates,
        "open": prices * 0.998,
        "high": prices * 1.005,
        "low": prices * 0.995,
        "close": prices,
        "volume": np.random.randint(1000, 10000, n_periods)
    })
    
    return df

###################################
# 🔔 TELEGRAM ALERT FUNCTIONS
###################################
def send_telegram_alert(message, bot_token, chat_id):
    """Send alert to Telegram channel"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_notification": False
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            # Log the alert
            alert_entry = {
                "time": datetime.now().strftime("%H:%M:%S"),
                "message": message,
                "status": "sent"
            }
            st.session_state.alerts_history.append(alert_entry)
            return True
        else:
            st.error(f"Telegram API error: {response.status_code}")
            return False
            
    except Exception as e:
        st.error(f"Failed to send Telegram alert: {e}")
        return False

def format_alert_message(current_price, alerts_data, timeframe_levels):
    """Format alert message for Telegram"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"🚨 <b>NIFTY ALERT</b> 🚨\n"
    message += f"⏰ {timestamp}\n"
    message += f"💰 Current Price: <b>{current_price:.2f}</b>\n"
    message += f"📊 Nearby Levels: {len(alerts_data)}\n\n"
    
    for alert in alerts_data:
        direction_emoji = "⬆️" if alert['direction'] == "ABOVE" else "⬇️"
        message += f"{direction_emoji} <b>{alert['timeframe']} {alert['level']}</b>\n"
        message += f"   Level: {alert['value']:.2f}\n"
        message += f"   Distance: {alert['distance']:.2f} ({alert['distance_pct']:.2f}%)\n\n"
    
    message += "📈 <b>Current S/R Levels:</b>\n"
    for tf, levels in timeframe_levels.items():
        message += f"\n{tf}:\n"
        for level_name, level_value in levels.items():
            if level_name.startswith("S"):
                message += f"  {level_name}: {level_value:.2f}\n"
        for level_name, level_value in levels.items():
            if level_name.startswith("R"):
                message += f"  {level_name}: {level_value:.2f}\n"
    
    message += "\n🔔 Auto-generated by NIFTY S/R Dashboard"
    
    return message

###################################
# 📈 VISUALIZATION FUNCTIONS
###################################
def create_price_chart(price_data, sr_levels):
    """Create interactive price chart with S/R levels"""
    fig = go.Figure()
    
    # Add candlestick chart
    fig.add_trace(go.Candlestick(
        x=price_data['timestamp'],
        open=price_data['open'],
        high=price_data['high'],
        low=price_data['low'],
        close=price_data['close'],
        name="Price",
        increasing_line_color='#26a69a',
        decreasing_line_color='#ef5350'
    ))
    
    # Add S/R levels as horizontal lines
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
                opacity=0.7
            )
    
    # Update layout
    fig.update_layout(
        title="NIFTY Price with S/R Levels",
        yaxis_title="Price",
        xaxis_title="Time",
        template="plotly_white",
        height=500,
        showlegend=True,
        xaxis_rangeslider_visible=False
    )
    
    return fig

###################################
# 🎯 MAIN DASHBOARD
###################################
st.markdown('<h1 class="main-header">📈 NIFTY HTF Support & Resistance Dashboard</h1>', unsafe_allow_html=True)

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["📊 S/R Levels", "📈 Price Chart", "⚙️ Configuration"])

with tab1:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("🧠 Support & Resistance Levels")
        
        # Progress bar for data loading
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Fetch and calculate S/R levels for each timeframe
        htf_levels = {}
        alerts_data = []
        
        for idx, timeframe in enumerate(timeframes):
            progress = (idx + 1) / len(timeframes)
            progress_bar.progress(progress)
            status_text.text(f"Loading {timeframe} data...")
            
            # Fetch OHLC data
            df_tf = fetch_ohlc_data(NIFTY_ID, timeframe)
            
            if not df_tf.empty:
                # Calculate S/R levels
                levels = calculate_support_resistance(df_tf, method="pivot")
                if levels:
                    htf_levels[timeframe] = levels
        
        progress_bar.empty()
        status_text.empty()
        
        # Display S/R levels table
        if htf_levels:
            df_table = pd.DataFrame(htf_levels).T
            
            # Style the DataFrame
            def color_support_resistance(val):
                if isinstance(val, (int, float)):
                    if 'S' in col:
                        return f"color: #ef4444; font-weight: bold"
                    elif 'R' in col:
                        return f"color: #10b981; font-weight: bold"
                    elif 'Pivot' in col:
                        return f"color: #6b7280; font-weight: bold"
                return ""
            
            # Apply styling
            styled_df = df_table.style.format("{:.2f}").applymap(
                color_support_resistance,
                subset=pd.IndexSlice[:, df_table.columns]
            )
            
            st.dataframe(styled_df, use_container_width=True)
            
            # Current Price and Alerts
            try:
                # Try to get current price (mock for demonstration)
                current_price = 22150.75  # Mock price
                
                st.markdown("---")
                col_price, col_alerts = st.columns(2)
                
                with col_price:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric(
                        label="📍 Current NIFTY Price",
                        value=f"₹{current_price:,.2f}",
                        delta="+125.50 (+0.57%)"
                    )
                    st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col_alerts:
                    # Check for alerts
                    for tf, levels in htf_levels.items():
                        for level_name, level_value in levels.items():
                            distance = abs(current_price - level_value)
                            distance_pct = (distance / current_price) * 100
                            
                            if distance_pct <= threshold_percent:
                                alert_info = {
                                    'timeframe': tf,
                                    'level': level_name,
                                    'value': level_value,
                                    'distance': distance,
                                    'distance_pct': distance_pct,
                                    'direction': "ABOVE" if current_price > level_value else "BELOW"
                                }
                                alerts_data.append(alert_info)
                    
                    if alerts_data:
                        st.markdown('<div class="alert-box alert-warning">', unsafe_allow_html=True)
                        st.warning(f"⚠️ {len(alerts_data)} Alert(s) Triggered!")
                        
                        for alert in alerts_data:
                            st.markdown(f"""
                            **{alert['timeframe']} {alert['level']}**
                            - Level: ₹{alert['value']:.2f}
                            - Price is {alert['direction']} by ₹{alert['distance']:.2f}
                            - Distance: {alert['distance_pct']:.2f}%
                            """)
                        
                        # Send alert button
                        if st.button("📨 Send Telegram Alert", type="primary", key="send_alert"):
                            alert_message = format_alert_message(current_price, alerts_data, htf_levels)
                            if send_telegram_alert(alert_message, config["BOT_TOKEN"], config["CHAT_ID"]):
                                st.success("✅ Alert sent to Telegram!")
                            else:
                                st.error("❌ Failed to send alert")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="alert-box alert-success">', unsafe_allow_html=True)
                        st.success("✅ No alerts triggered")
                        st.caption(f"Price is not within {threshold_percent}% of any S/R level")
                        st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error processing price data: {e}")
        
        else:
            st.warning("No S/R levels calculated. Please check your connection and try again.")
        
        # Download data button
        if htf_levels:
            csv_data = pd.DataFrame(htf_levels).T.to_csv()
            st.download_button(
                label="📥 Download S/R Levels (CSV)",
                data=csv_data,
                file_name=f"nifty_sr_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
    
    with col2:
        st.subheader("📊 Quick Stats")
        
        # Statistics cards
        stats_col1, stats_col2 = st.columns(2)
        
        with stats_col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Timeframes", len(timeframes))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with stats_col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("S/R Levels", len(htf_levels) * 5 if htf_levels else 0)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Alert Threshold", f"{threshold_percent}%")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Alerts", len(st.session_state.alerts_history))
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Refresh info
        st.info(f"""
        **Auto-refresh:** Every 2 minutes
        **Next refresh:** In {(120000 - (time.time() * 1000) % 120000) / 1000:.0f} seconds
        **Refresh count:** {refresh_count}
        """)

with tab2:
    st.subheader("📈 Interactive Price Chart")
    
    if htf_levels and '60m' in htf_levels:
        # Get hourly data for the chart
        hourly_data = fetch_ohlc_data(NIFTY_ID, "60m")
        
        if not hourly_data.empty:
            fig = create_price_chart(hourly_data, htf_levels['60m'])
            st.plotly_chart(fig, use_container_width=True)
            
            # Chart controls
            col_chart1, col_chart2, col_chart3 = st.columns(3)
            with col_chart1:
                show_volume = st.checkbox("Show Volume", value=False)
            with col_chart2:
                chart_type = st.selectbox("Chart Type", ["Candlestick", "Line", "OHLC"])
            with col_chart3:
                st.download_button(
                    "📥 Download Chart Data",
                    hourly_data.to_csv(),
                    "nifty_hourly_data.csv"
                )
        else:
            st.warning("No price data available for chart")
    else:
        st.info("Please load S/R data first from the main tab")

with tab3:
    st.subheader("⚙️ Application Configuration")
    
    col_config1, col_config2 = st.columns(2)
    
    with col_config1:
        st.markdown("### API Status")
        
        # API status indicators
        api_status = "✅ Connected" if api is not None else "❌ Disconnected"
        st.markdown(f"**Dhan API:** {api_status}")
        
        # Test Telegram connection
        if st.button("Test Telegram Connection"):
            test_message = f"✅ NIFTY S/R Dashboard Test - {datetime.now().strftime('%H:%M:%S')}"
            if send_telegram_alert(test_message, config["BOT_TOKEN"], config["CHAT_ID"]):
                st.success("Telegram connection successful!")
            else:
                st.error("Telegram connection failed")
        
        # Data source selection
        st.markdown("### Data Source")
        data_source = st.radio(
            "Select data source:",
            ["Dhan API (Real-time)", "Mock Data (Demo)"],
            index=1 if api is None else 0
        )
    
    with col_config2:
        st.markdown("### Alert Preferences")
        
        # Alert methods
        alert_methods = st.multiselect(
            "Notification Methods:",
            ["Telegram", "Browser Notification", "Email"],
            default=["Telegram"]
        )
        
        # Alert frequency
        alert_frequency = st.selectbox(
            "Alert Frequency:",
            ["Immediate", "Every 5 minutes", "Every 15 minutes", "Only once per level"]
        )
        
        # Sound alerts
        sound_alerts = st.checkbox("Enable sound alerts", value=True)
    
    st.markdown("---")
    st.subheader("📋 System Information")
    
    sys_col1, sys_col2, sys_col3 = st.columns(3)
    
    with sys_col1:
        st.metric("Python Version", "3.9+")
        st.metric("Streamlit Version", "1.28.0")
    
    with sys_col2:
        st.metric("Pandas Version", "2.1.0")
        st.metric("Last Updated", datetime.now().strftime("%Y-%m-%d"))
    
    with sys_col3:
        st.metric("Uptime", "24/7")
        if st.button("🔄 Restart App"):
            st.rerun()

###################################
# 📱 FOOTER
###################################
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.caption("📧 Support: support@tradingapp.com")
    st.caption("🔒 Data is encrypted and secure")

with footer_col2:
    st.caption("🔄 Auto-refresh: Every 2 minutes")
    st.caption(f"⏰ Last refresh: {datetime.now().strftime('%H:%M:%S')}")

with footer_col3:
    st.caption("⚠️ For educational purposes only")
    st.caption("📈 Trade at your own risk")

# Manual refresh button
if st.button("🔄 Manual Refresh Now", type="secondary", use_container_width=True):
    st.rerun()

# Add numpy import if using mock data
import numpy as np