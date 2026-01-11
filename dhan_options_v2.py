import streamlit as st
import pandas as pd
from dhanhq import dhanhq
import requests
import time
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Dhan Options Platform v2.0",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .call-side {
        background-color: #e8f5e9;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .put-side {
        background-color: #ffebee;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .atm-strike {
        background-color: #fff9c4;
        font-weight: bold;
        padding: 15px;
        border-radius: 5px;
    }
    .positive {
        color: #2e7d32;
    }
    .negative {
        color: #c62828;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'dhan' not in st.session_state:
    st.session_state.dhan = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'client_id' not in st.session_state:
    st.session_state.client_id = None
if 'access_token' not in st.session_state:
    st.session_state.access_token = None

# API Base URL
DHAN_API_BASE = "https://api.dhan.co/v2"

# Sidebar - Authentication
with st.sidebar:
    st.title("🔐 Dhan API v2.0 Login")
    
    if not st.session_state.logged_in:
        st.markdown("### Enter Credentials")
        client_id = st.text_input("Client ID", type="password", key="input_client_id")
        access_token = st.text_input("Access Token", type="password", key="input_access_token")
        
        if st.button("Login to Dhan", type="primary"):
            if client_id and access_token:
                try:
                    # Test connection with User Profile API
                    headers = {
                        'access-token': access_token,
                        'Content-Type': 'application/json'
                    }
                    response = requests.get(f"{DHAN_API_BASE}/profile", headers=headers)
                    
                    if response.status_code == 200:
                        profile = response.json()
                        st.session_state.dhan = dhanhq(client_id, access_token)
                        st.session_state.logged_in = True
                        st.session_state.client_id = client_id
                        st.session_state.access_token = access_token
                        st.success(f"✅ Welcome {profile.get('dhanClientId', 'User')}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ Login failed: {response.text}")
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")
            else:
                st.warning("⚠️ Please enter both credentials")
        
        st.divider()
        st.markdown("""
        ### 📝 How to get credentials:
        1. Login to [web.dhan.co](https://web.dhan.co)
        2. Go to **My Profile**
        3. Navigate to **'Access DhanHQ APIs'**
        4. Generate **Access Token**
        5. Copy **Client ID** and **Access Token**
        """)
    else:
        st.success("✅ Connected to Dhan")
        
        # User profile info
        try:
            headers = {
                'access-token': st.session_state.access_token,
                'Content-Type': 'application/json'
            }
            response = requests.get(f"{DHAN_API_BASE}/profile", headers=headers)
            if response.status_code == 200:
                profile = response.json()
                st.info(f"**Client ID:** {profile.get('dhanClientId')}")
                st.info(f"**Token Valid Till:** {profile.get('tokenValidity')}")
        except:
            pass
        
        if st.button("Logout", type="secondary"):
            st.session_state.dhan = None
            st.session_state.logged_in = False
            st.session_state.client_id = None
            st.session_state.access_token = None
            st.rerun()
        
        st.divider()
        
        # Settings
        st.markdown("### ⚙️ Settings")
        num_strikes = st.slider("Strikes to Display", 3, 10, 5, key="num_strikes")
        auto_refresh = st.checkbox("Auto Refresh (10s)", value=False)

# Main content
st.title("📊 Dhan Options Trading Platform")
st.markdown("### NIFTY & SENSEX Options Chain Analysis")

if not st.session_state.logged_in:
    st.warning("⚠️ Please login using the sidebar to access the platform")
    st.info("""
    ### Quick Start:
    1. Get your Dhan API credentials from web.dhan.co
    2. Enter Client ID and Access Token in the sidebar
    3. Click "Login to Dhan"
    4. Start analyzing options!
    """)
    st.stop()

# Helper functions
def get_market_quote(security_id, exchange_segment):
    """Fetch market quote using Dhan API v2.0"""
    try:
        # Using dhanhq library
        if st.session_state.dhan:
            quote = st.session_state.dhan.get_market_quote(
                security_id=security_id,
                exchange_segment=exchange_segment
            )
            return quote
        return None
    except Exception as e:
        st.error(f"Error fetching quote: {str(e)}")
        return None

def get_atm_strike(spot_price, strike_diff):
    """Calculate ATM strike price"""
    return round(spot_price / strike_diff) * strike_diff

def get_strike_range(atm_strike, strike_diff, num_strikes):
    """Get strike range ATM ±num_strikes"""
    strikes = []
    for i in range(-num_strikes, num_strikes + 1):
        strikes.append(atm_strike + (i * strike_diff))
    return strikes

def format_change(value):
    """Format change value with color"""
    if value > 0:
        return f"<span class='positive'>+{value:.2f}%</span>"
    elif value < 0:
        return f"<span class='negative'>{value:.2f}%</span>"
    else:
        return f"{value:.2f}%"

def display_option_data(ltp, volume, oi, change, bid, ask):
    """Display option data in formatted way"""
    return f"""
    <div>
        <b>LTP:</b> ₹{ltp:,.2f} | <b>Chg:</b> {format_change(change)}<br>
        <b>Volume:</b> {volume:,} | <b>OI:</b> {oi:,}<br>
        <b>Bid:</b> ₹{bid:,.2f} | <b>Ask:</b> ₹{ask:,.2f}
    </div>
    """

# Tabs
tab1, tab2, tab3 = st.tabs(["📈 NIFTY 50", "📊 SENSEX", "📋 Order Book"])

with tab1:
    st.subheader("NIFTY 50 Options Chain")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Get NIFTY spot price
    nifty_spot = 23500  # Default
    try:
        # NIFTY 50 Index security ID
        quote = get_market_quote("13", "IDX_I")
        if quote and 'data' in quote:
            nifty_spot = quote['data'].get('LTP', 23500)
        col1.metric("NIFTY Spot", f"₹{nifty_spot:,.2f}")
    except:
        col1.metric("NIFTY Spot", f"₹{nifty_spot:,.2f}", "Demo Mode")
    
    # Calculate ATM
    nifty_atm = get_atm_strike(nifty_spot, 50)
    col2.metric("ATM Strike", nifty_atm)
    
    # Expiry input
    expiry_nifty = col3.text_input("Expiry (DDMMMYY)", "16JAN26", key="nifty_expiry")
    
    # Refresh button
    if col4.button("🔄 Refresh NIFTY", key="btn_refresh_nifty"):
        st.rerun()
    
    st.markdown("---")
    
    # Generate strikes
    nifty_strikes = get_strike_range(nifty_atm, 50, st.session_state.get('num_strikes', 5))
    
    # Display header
    col_call, col_strike, col_put = st.columns([4, 2, 4])
    with col_call:
        st.markdown("### 📞 CALL Options")
    with col_strike:
        st.markdown("### Strike Price")
    with col_put:
        st.markdown("### 📉 PUT Options")
    
    st.markdown("---")
    
    # Display options chain
    for strike in nifty_strikes:
        col_call, col_strike, col_put = st.columns([4, 2, 4])
        
        is_atm = (strike == nifty_atm)
        
        with col_call:
            # Call option data (demo)
            call_html = f"""
            <div class='call-side'>
                {display_option_data(100.50, 125000, 2500000, 2.5, 100.25, 100.75)}
            </div>
            """
            st.markdown(call_html, unsafe_allow_html=True)
        
        with col_strike:
            if is_atm:
                st.markdown(f"<div class='atm-strike'>{strike}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align: center; padding: 15px;'><b>{strike}</b></div>", unsafe_allow_html=True)
        
        with col_put:
            # Put option data (demo)
            put_html = f"""
            <div class='put-side'>
                {display_option_data(85.25, 98000, 1800000, -1.2, 85.00, 85.50)}
            </div>
            """
            st.markdown(put_html, unsafe_allow_html=True)
    
    # PCR Analysis
    st.markdown("---")
    st.markdown("### 📊 Put-Call Ratio Analysis")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Call OI", "15.2 Cr")
    col2.metric("Total Put OI", "18.5 Cr")
    col3.metric("PCR Ratio", "1.22", "Bearish")
    col4.metric("Max Pain", "23500")

with tab2:
    st.subheader("SENSEX Options Chain")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Get SENSEX spot price
    sensex_spot = 77000  # Default
    try:
        # SENSEX Index security ID
        quote = get_market_quote("51", "BSE_IDX")
        if quote and 'data' in quote:
            sensex_spot = quote['data'].get('LTP', 77000)
        col1.metric("SENSEX Spot", f"₹{sensex_spot:,.2f}")
    except:
        col1.metric("SENSEX Spot", f"₹{sensex_spot:,.2f}", "Demo Mode")
    
    # Calculate ATM
    sensex_atm = get_atm_strike(sensex_spot, 100)
    col2.metric("ATM Strike", sensex_atm)
    
    # Expiry input
    expiry_sensex = col3.text_input("Expiry (DDMMMYY)", "16JAN26", key="sensex_expiry")
    
    # Refresh button
    if col4.button("🔄 Refresh SENSEX", key="btn_refresh_sensex"):
        st.rerun()
    
    st.markdown("---")
    
    # Generate strikes
    sensex_strikes = get_strike_range(sensex_atm, 100, st.session_state.get('num_strikes', 5))
    
    # Display header
    col_call, col_strike, col_put = st.columns([4, 2, 4])
    with col_call:
        st.markdown("### 📞 CALL Options")
    with col_strike:
        st.markdown("### Strike Price")
    with col_put:
        st.markdown("### 📉 PUT Options")
    
    st.markdown("---")
    
    # Display options chain
    for strike in sensex_strikes:
        col_call, col_strike, col_put = st.columns([4, 2, 4])
        
        is_atm = (strike == sensex_atm)
        
        with col_call:
            call_html = f"""
            <div class='call-side'>
                {display_option_data(220.50, 85000, 1500000, 1.8, 220.00, 221.00)}
            </div>
            """
            st.markdown(call_html, unsafe_allow_html=True)
        
        with col_strike:
            if is_atm:
                st.markdown(f"<div class='atm-strike'>{strike}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align: center; padding: 15px;'><b>{strike}</b></div>", unsafe_allow_html=True)
        
        with col_put:
            put_html = f"""
            <div class='put-side'>
                {display_option_data(195.75, 72000, 1200000, -0.8, 195.50, 196.00)}
            </div>
            """
            st.markdown(put_html, unsafe_allow_html=True)
    
    # PCR Analysis
    st.markdown("---")
    st.markdown("### 📊 Put-Call Ratio Analysis")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Call OI", "8.5 Cr")
    col2.metric("Total Put OI", "9.2 Cr")
    col3.metric("PCR Ratio", "1.08", "Neutral")
    col4.metric("Max Pain", "77000")

with tab3:
    st.subheader("📋 Order Book")
    
    if st.button("🔄 Refresh Orders"):
        st.rerun()
    
    try:
        # Fetch orders using API
        headers = {
            'access-token': st.session_state.access_token,
            'Content-Type': 'application/json'
        }
        response = requests.get(f"{DHAN_API_BASE}/orders", headers=headers)
        
        if response.status_code == 200:
            orders = response.json()
            if orders:
                # Display orders in table
                df_orders = pd.DataFrame(orders)
                st.dataframe(df_orders, use_container_width=True)
            else:
                st.info("No orders placed today")
        else:
            st.warning("Unable to fetch orders")
    except Exception as e:
        st.error(f"Error fetching orders: {str(e)}")

# Auto refresh
if st.session_state.get('auto_refresh', False):
    time.sleep(10)
    st.rerun()

# Footer
st.markdown("---")
st.markdown(f"""
    <div style='text-align: center; color: gray; font-size: 12px;'>
        <p>📊 Dhan Options Platform v2.0 | Powered by Dhan API</p>
        <p>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>⚠️ For educational purposes only. Trade at your own risk.</p>
    </div>
""", unsafe_allow_html=True)
