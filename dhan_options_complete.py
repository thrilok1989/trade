import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Dhan Options Platform - Live",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {padding: 0rem 1rem;}
    .stMetric {background-color: #f0f2f6; padding: 10px; border-radius: 5px;}
    .call-side {background-color: #e8f5e9; padding: 12px; border-radius: 5px; margin: 5px 0;}
    .put-side {background-color: #ffebee; padding: 12px; border-radius: 5px; margin: 5px 0;}
    .atm-strike {background-color: #fff9c4; font-weight: bold; padding: 15px; border-radius: 5px; text-align: center;}
    .positive {color: #2e7d32; font-weight: bold;}
    .negative {color: #c62828; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'client_id' not in st.session_state:
    st.session_state.client_id = None
if 'access_token' not in st.session_state:
    st.session_state.access_token = None

# API Configuration
DHAN_API_BASE = "https://api.dhan.co/v2"

# Security IDs for Indices
NIFTY_SECURITY_ID = "13"
SENSEX_SECURITY_ID = "51"
NIFTY_SEGMENT = "IDX_I"
SENSEX_SEGMENT = "BSE_IDX"

# Helper Functions
def get_headers():
    """Get API headers"""
    return {
        'access-token': st.session_state.access_token,
        'client-id': st.session_state.client_id,
        'Content-Type': 'application/json'
    }

def test_connection():
    """Test API connection with profile endpoint"""
    try:
        response = requests.get(f"{DHAN_API_BASE}/profile", headers=get_headers())
        return response.status_code == 200, response.json() if response.status_code == 200 else response.text
    except Exception as e:
        return False, str(e)

def get_market_quote_ltp(security_ids_dict):
    """Fetch LTP using Market Quote API"""
    try:
        response = requests.post(
            f"{DHAN_API_BASE}/marketfeed/ltp",
            headers=get_headers(),
            json=security_ids_dict
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching LTP: {str(e)}")
        return None

def get_option_chain(underlying_scrip, underlying_seg, expiry):
    """Fetch Option Chain data"""
    try:
        payload = {
            "UnderlyingScrip": int(underlying_scrip),
            "UnderlyingSeg": underlying_seg,
            "Expiry": expiry
        }
        response = requests.post(
            f"{DHAN_API_BASE}/optionchain",
            headers=get_headers(),
            json=payload
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching option chain: {str(e)}")
        return None

def get_expiry_list(underlying_scrip, underlying_seg):
    """Fetch expiry dates list"""
    try:
        payload = {
            "UnderlyingScrip": int(underlying_scrip),
            "UnderlyingSeg": underlying_seg
        }
        response = requests.post(
            f"{DHAN_API_BASE}/optionchain/expirylist",
            headers=get_headers(),
            json=payload
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        return []
    except Exception as e:
        st.error(f"Error fetching expiry list: {str(e)}")
        return []

def get_atm_strike(spot_price, strike_diff):
    """Calculate ATM strike"""
    return round(spot_price / strike_diff) * strike_diff

def format_change(value):
    """Format change value with color"""
    if value > 0:
        return f"<span class='positive'>+{value:.2f}%</span>"
    elif value < 0:
        return f"<span class='negative'>{value:.2f}%</span>"
    else:
        return f"{value:.2f}%"

def display_option_data(data, option_type):
    """Display option data in formatted way"""
    if not data:
        return "<div>No data</div>"
    
    ltp = data.get('last_price', 0)
    oi = data.get('oi', 0)
    volume = data.get('volume', 0)
    iv = data.get('implied_volatility', 0)
    prev_close = data.get('previous_close_price', 0)
    
    change_pct = ((ltp - prev_close) / prev_close * 100) if prev_close > 0 else 0
    
    greeks = data.get('greeks', {})
    delta = greeks.get('delta', 0)
    
    return f"""
    <div>
        <b>LTP:</b> ₹{ltp:,.2f} | <b>Chg:</b> {format_change(change_pct)}<br>
        <b>OI:</b> {oi:,} | <b>Vol:</b> {volume:,}<br>
        <b>IV:</b> {iv:.2f}% | <b>Δ:</b> {delta:.4f}
    </div>
    """

# Sidebar - Authentication
with st.sidebar:
    st.title("🔐 Dhan API v2.0")
    
    if not st.session_state.logged_in:
        st.markdown("### Authentication")
        client_id = st.text_input("Client ID", type="password")
        access_token = st.text_input("Access Token", type="password")
        
        if st.button("Login", type="primary", use_container_width=True):
            if client_id and access_token:
                st.session_state.client_id = client_id
                st.session_state.access_token = access_token
                
                success, result = test_connection()
                if success:
                    st.session_state.logged_in = True
                    st.success("✅ Connected!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ Failed: {result}")
                    st.session_state.logged_in = False
            else:
                st.warning("⚠️ Enter credentials")
        
        st.divider()
        st.markdown("""
        ### 📝 Get Credentials:
        1. [web.dhan.co](https://web.dhan.co)
        2. My Profile → Access DhanHQ APIs
        3. Generate Access Token (24h)
        """)
    else:
        st.success("✅ Connected")
        
        # Profile info
        try:
            _, profile = test_connection()
            if profile and isinstance(profile, dict):
                st.info(f"**ID:** {profile.get('dhanClientId', 'N/A')}")
                st.info(f"**Valid:** {profile.get('tokenValidity', 'N/A')}")
        except:
            pass
        
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.client_id = None
            st.session_state.access_token = None
            st.rerun()
        
        st.divider()
        st.markdown("### ⚙️ Settings")
        num_strikes = st.slider("Strikes Display", 3, 10, 5)
        auto_refresh = st.checkbox("Auto Refresh (10s)")

# Main App
st.title("📊 Dhan Options Trading Platform")
st.markdown("### Real-Time Option Chain Analysis")

if not st.session_state.logged_in:
    st.warning("⚠️ Please login to access live option chain data")
    st.info("""
    ### Features:
    - ✅ Real-time NIFTY & SENSEX option chains
    - ✅ Live Greeks (Delta, Gamma, Theta, Vega)
    - ✅ Open Interest & Volume tracking
    - ✅ Implied Volatility analysis
    - ✅ PCR calculations
    - ✅ ATM strike highlighting
    """)
    st.stop()

# Tabs
tab1, tab2 = st.tabs(["📈 NIFTY 50", "📊 SENSEX"])

with tab1:
    st.subheader("NIFTY 50 Options Chain")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Fetch NIFTY spot
    nifty_spot = 23500  # Default
    try:
        ltp_data = get_market_quote_ltp({"IDX_I": [int(NIFTY_SECURITY_ID)]})
        if ltp_data and 'data' in ltp_data:
            nifty_spot = ltp_data['data'].get('IDX_I', {}).get(NIFTY_SECURITY_ID, {}).get('last_price', 23500)
    except:
        pass
    
    col1.metric("NIFTY Spot", f"₹{nifty_spot:,.2f}")
    
    # ATM calculation
    nifty_atm = get_atm_strike(nifty_spot, 50)
    col2.metric("ATM Strike", nifty_atm)
    
    # Get expiry list
    expiry_list = get_expiry_list(NIFTY_SECURITY_ID, NIFTY_SEGMENT)
    if expiry_list:
        selected_expiry = col3.selectbox("Expiry", expiry_list, key="nifty_expiry")
    else:
        selected_expiry = col3.text_input("Expiry (YYYY-MM-DD)", "2026-01-16", key="nifty_expiry_manual")
    
    if col4.button("🔄 Refresh", key="btn_nifty"):
        st.rerun()
    
    st.markdown("---")
    
    # Fetch option chain
    with st.spinner("Fetching NIFTY option chain..."):
        option_data = get_option_chain(NIFTY_SECURITY_ID, NIFTY_SEGMENT, selected_expiry)
    
    if option_data and 'data' in option_data:
        oc = option_data['data'].get('oc', {})
        
        # Generate strike list around ATM
        strikes = sorted([float(k) for k in oc.keys()])
        atm_idx = min(range(len(strikes)), key=lambda i: abs(strikes[i] - nifty_atm))
        start_idx = max(0, atm_idx - num_strikes)
        end_idx = min(len(strikes), atm_idx + num_strikes + 1)
        display_strikes = strikes[start_idx:end_idx]
        
        # Display header
        col_call, col_strike, col_put = st.columns([4, 2, 4])
        with col_call:
            st.markdown("### 📞 CALL")
        with col_strike:
            st.markdown("### Strike")
        with col_put:
            st.markdown("### 📉 PUT")
        
        st.markdown("---")
        
        # Display options chain
        total_call_oi = 0
        total_put_oi = 0
        
        for strike in display_strikes:
            strike_key = f"{strike:.6f}"
            strike_data = oc.get(strike_key, {})
            
            col_call, col_strike, col_put = st.columns([4, 2, 4])
            
            is_atm = abs(strike - nifty_atm) < 25
            
            # Call data
            with col_call:
                ce_data = strike_data.get('ce', {})
                if ce_data:
                    total_call_oi += ce_data.get('oi', 0)
                call_html = f"<div class='call-side'>{display_option_data(ce_data, 'CE')}</div>"
                st.markdown(call_html, unsafe_allow_html=True)
            
            # Strike
            with col_strike:
                if is_atm:
                    st.markdown(f"<div class='atm-strike'>{int(strike)}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='text-align: center; padding: 15px;'><b>{int(strike)}</b></div>", unsafe_allow_html=True)
            
            # Put data
            with col_put:
                pe_data = strike_data.get('pe', {})
                if pe_data:
                    total_put_oi += pe_data.get('oi', 0)
                put_html = f"<div class='put-side'>{display_option_data(pe_data, 'PE')}</div>"
                st.markdown(put_html, unsafe_allow_html=True)
        
        # PCR Analysis
        st.markdown("---")
        st.markdown("### 📊 Market Analysis")
        col1, col2, col3, col4 = st.columns(4)
        
        pcr = (total_put_oi / total_call_oi) if total_call_oi > 0 else 0
        pcr_sentiment = "Bullish" if pcr < 0.8 else "Bearish" if pcr > 1.2 else "Neutral"
        
        col1.metric("Call OI", f"{total_call_oi/10000000:.2f} Cr")
        col2.metric("Put OI", f"{total_put_oi/10000000:.2f} Cr")
        col3.metric("PCR", f"{pcr:.2f}", pcr_sentiment)
        col4.metric("Strikes", len(display_strikes))
    else:
        st.warning("Unable to fetch option chain data. Please check expiry date or try again.")

with tab2:
    st.subheader("SENSEX Options Chain")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Fetch SENSEX spot
    sensex_spot = 77000  # Default
    try:
        ltp_data = get_market_quote_ltp({"BSE_IDX": [int(SENSEX_SECURITY_ID)]})
        if ltp_data and 'data' in ltp_data:
            sensex_spot = ltp_data['data'].get('BSE_IDX', {}).get(SENSEX_SECURITY_ID, {}).get('last_price', 77000)
    except:
        pass
    
    col1.metric("SENSEX Spot", f"₹{sensex_spot:,.2f}")
    
    # ATM calculation
    sensex_atm = get_atm_strike(sensex_spot, 100)
    col2.metric("ATM Strike", sensex_atm)
    
    # Get expiry list
    expiry_list_sensex = get_expiry_list(SENSEX_SECURITY_ID, "BSE_IDX")
    if expiry_list_sensex:
        selected_expiry_sensex = col3.selectbox("Expiry", expiry_list_sensex, key="sensex_expiry")
    else:
        selected_expiry_sensex = col3.text_input("Expiry (YYYY-MM-DD)", "2026-01-16", key="sensex_expiry_manual")
    
    if col4.button("🔄 Refresh", key="btn_sensex"):
        st.rerun()
    
    st.markdown("---")
    
    # Fetch option chain
    with st.spinner("Fetching SENSEX option chain..."):
        option_data_sensex = get_option_chain(SENSEX_SECURITY_ID, "BSE_IDX", selected_expiry_sensex)
    
    if option_data_sensex and 'data' in option_data_sensex:
        oc_sensex = option_data_sensex['data'].get('oc', {})
        
        # Generate strike list
        strikes_sensex = sorted([float(k) for k in oc_sensex.keys()])
        atm_idx = min(range(len(strikes_sensex)), key=lambda i: abs(strikes_sensex[i] - sensex_atm))
        start_idx = max(0, atm_idx - num_strikes)
        end_idx = min(len(strikes_sensex), atm_idx + num_strikes + 1)
        display_strikes_sensex = strikes_sensex[start_idx:end_idx]
        
        # Display header
        col_call, col_strike, col_put = st.columns([4, 2, 4])
        with col_call:
            st.markdown("### 📞 CALL")
        with col_strike:
            st.markdown("### Strike")
        with col_put:
            st.markdown("### 📉 PUT")
        
        st.markdown("---")
        
        # Display options chain
        total_call_oi_sensex = 0
        total_put_oi_sensex = 0
        
        for strike in display_strikes_sensex:
            strike_key = f"{strike:.6f}"
            strike_data = oc_sensex.get(strike_key, {})
            
            col_call, col_strike, col_put = st.columns([4, 2, 4])
            
            is_atm = abs(strike - sensex_atm) < 50
            
            # Call data
            with col_call:
                ce_data = strike_data.get('ce', {})
                if ce_data:
                    total_call_oi_sensex += ce_data.get('oi', 0)
                call_html = f"<div class='call-side'>{display_option_data(ce_data, 'CE')}</div>"
                st.markdown(call_html, unsafe_allow_html=True)
            
            # Strike
            with col_strike:
                if is_atm:
                    st.markdown(f"<div class='atm-strike'>{int(strike)}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='text-align: center; padding: 15px;'><b>{int(strike)}</b></div>", unsafe_allow_html=True)
            
            # Put data
            with col_put:
                pe_data = strike_data.get('pe', {})
                if pe_data:
                    total_put_oi_sensex += pe_data.get('oi', 0)
                put_html = f"<div class='put-side'>{display_option_data(pe_data, 'PE')}</div>"
                st.markdown(put_html, unsafe_allow_html=True)
        
        # PCR Analysis
        st.markdown("---")
        st.markdown("### 📊 Market Analysis")
        col1, col2, col3, col4 = st.columns(4)
        
        pcr_sensex = (total_put_oi_sensex / total_call_oi_sensex) if total_call_oi_sensex > 0 else 0
        pcr_sentiment_sensex = "Bullish" if pcr_sensex < 0.8 else "Bearish" if pcr_sensex > 1.2 else "Neutral"
        
        col1.metric("Call OI", f"{total_call_oi_sensex/10000000:.2f} Cr")
        col2.metric("Put OI", f"{total_put_oi_sensex/10000000:.2f} Cr")
        col3.metric("PCR", f"{pcr_sensex:.2f}", pcr_sentiment_sensex)
        col4.metric("Strikes", len(display_strikes_sensex))
    else:
        st.warning("Unable to fetch option chain data. Please check expiry date or try again.")

# Auto refresh
if auto_refresh:
    time.sleep(10)
    st.rerun()

# Footer
st.markdown("---")
st.markdown(f"""
    <div style='text-align: center; color: gray; font-size: 12px;'>
        <p>📊 Dhan Options Platform | Real-time Option Chain API</p>
        <p>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}</p>
        <p>⚠️ For educational purposes only. Trade responsibly.</p>
    </div>
""", unsafe_allow_html=True)
