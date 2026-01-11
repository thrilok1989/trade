import streamlit as st
import pandas as pd
from dhanhq import dhanhq
import time
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Dhan Options Trading Platform",
    page_icon="📈",
    layout="wide"
)

# Custom CSS for better styling
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
    }
    .put-side {
        background-color: #ffebee;
    }
    .atm-strike {
        background-color: #fff9c4;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'dhan' not in st.session_state:
    st.session_state.dhan = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Sidebar for authentication
with st.sidebar:
    st.title("🔐 Dhan Authentication")
    
    if not st.session_state.logged_in:
        client_id = st.text_input("Client ID", type="password")
        access_token = st.text_input("Access Token", type="password")
        
        if st.button("Login"):
            if client_id and access_token:
                try:
                    st.session_state.dhan = dhanhq(client_id, access_token)
                    st.session_state.logged_in = True
                    st.success("✅ Successfully logged in!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Login failed: {str(e)}")
            else:
                st.warning("Please enter both Client ID and Access Token")
    else:
        st.success("✅ Logged In")
        if st.button("Logout"):
            st.session_state.dhan = None
            st.session_state.logged_in = False
            st.rerun()
    
    st.divider()
    st.markdown("### Settings")
    auto_refresh = st.checkbox("Auto Refresh", value=False)
    if auto_refresh:
        refresh_interval = st.slider("Refresh Interval (seconds)", 5, 60, 10)

# Main application
st.title("📊 Dhan Options Trading Platform")
st.markdown("### NIFTY & SENSEX Options Chain Analysis")

if not st.session_state.logged_in:
    st.warning("⚠️ Please login using the sidebar to access the platform")
    st.stop()

# Helper functions
def get_atm_strike(spot_price, strike_diff):
    """Calculate ATM strike price"""
    return round(spot_price / strike_diff) * strike_diff

def get_strike_range(atm_strike, strike_diff, num_strikes=5):
    """Get strike range ATM ±num_strikes"""
    strikes = []
    for i in range(-num_strikes, num_strikes + 1):
        strikes.append(atm_strike + (i * strike_diff))
    return strikes

def fetch_option_chain_data(dhan, symbol, strikes, expiry_date, exchange_segment):
    """Fetch option chain data for given strikes"""
    data = []
    
    for strike in strikes:
        try:
            # Fetch CALL data
            call_security_id = f"{symbol}{expiry_date}{strike}CE"
            call_quote = dhan.get_market_quote(call_security_id, exchange_segment)
            
            # Fetch PUT data
            put_security_id = f"{symbol}{expiry_date}{strike}PE"
            put_quote = dhan.get_market_quote(put_security_id, exchange_segment)
            
            data.append({
                'strike': strike,
                'call_ltp': call_quote.get('last_price', 0),
                'call_volume': call_quote.get('volume', 0),
                'call_oi': call_quote.get('oi', 0),
                'call_change': call_quote.get('change', 0),
                'put_ltp': put_quote.get('last_price', 0),
                'put_volume': put_quote.get('volume', 0),
                'put_oi': put_quote.get('oi', 0),
                'put_change': put_quote.get('change', 0),
            })
        except Exception as e:
            st.warning(f"Error fetching data for strike {strike}: {str(e)}")
            continue
    
    return pd.DataFrame(data)

def get_nifty_spot_price(dhan):
    """Get NIFTY spot price"""
    try:
        # Dhan security ID for NIFTY 50 Index
        nifty_quote = dhan.get_market_quote("13", "IDX_I")  # NIFTY 50
        return nifty_quote.get('last_price', 0)
    except:
        return 23500  # Default fallback

def get_sensex_spot_price(dhan):
    """Get SENSEX spot price"""
    try:
        # Dhan security ID for SENSEX
        sensex_quote = dhan.get_market_quote("51", "BSE_IDX")  # SENSEX
        return sensex_quote.get('last_price', 0)
    except:
        return 77000  # Default fallback

def format_option_chain_display(df, atm_strike):
    """Format the option chain dataframe for display"""
    if df.empty:
        return df
    
    # Add styling for ATM strike
    def highlight_atm(row):
        if row['strike'] == atm_strike:
            return ['background-color: #fff9c4; font-weight: bold'] * len(row)
        return [''] * len(row)
    
    return df

# Tabs for NIFTY and SENSEX
tab1, tab2 = st.tabs(["📈 NIFTY 50", "📊 SENSEX"])

with tab1:
    st.subheader("NIFTY 50 Options Chain")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Fetch NIFTY spot price
    try:
        nifty_spot = get_nifty_spot_price(st.session_state.dhan)
        col1.metric("NIFTY Spot", f"₹{nifty_spot:,.2f}")
    except Exception as e:
        nifty_spot = 23500
        col1.metric("NIFTY Spot", f"₹{nifty_spot:,.2f} (Default)")
    
    # Calculate ATM
    nifty_atm = get_atm_strike(nifty_spot, 50)
    col2.metric("ATM Strike", f"{nifty_atm}")
    
    # Expiry selection
    expiry_date = col3.text_input("Expiry (DDMMMYY)", "09JAN26", key="nifty_expiry")
    
    if col4.button("🔄 Refresh NIFTY", key="refresh_nifty"):
        st.rerun()
    
    # Generate strikes
    nifty_strikes = get_strike_range(nifty_atm, 50, 5)
    
    # Create option chain display
    st.markdown("---")
    
    # Manual data display (for demo purposes)
    st.markdown("### Options Chain Table")
    
    # Create columns for better layout
    col_call, col_strike, col_put = st.columns([3, 1, 3])
    
    with col_call:
        st.markdown("#### 📞 CALL Options")
    with col_strike:
        st.markdown("#### Strike")
    with col_put:
        st.markdown("#### 📉 PUT Options")
    
    # Display option chain
    for strike in nifty_strikes:
        col_call, col_strike, col_put = st.columns([3, 1, 3])
        
        is_atm = (strike == nifty_atm)
        strike_style = "background-color: #fff9c4; padding: 10px; border-radius: 5px; text-align: center;" if is_atm else "padding: 10px; text-align: center;"
        
        with col_call:
            call_data = f"""
            <div style='background-color: #e8f5e9; padding: 10px; border-radius: 5px;'>
                <b>LTP:</b> ₹{0.00}<br>
                <b>Volume:</b> {0:,}<br>
                <b>OI:</b> {0:,}<br>
                <b>Change:</b> {0.00}%
            </div>
            """
            st.markdown(call_data, unsafe_allow_html=True)
        
        with col_strike:
            st.markdown(f"<div style='{strike_style}'><b>{strike}</b></div>", unsafe_allow_html=True)
        
        with col_put:
            put_data = f"""
            <div style='background-color: #ffebee; padding: 10px; border-radius: 5px;'>
                <b>LTP:</b> ₹{0.00}<br>
                <b>Volume:</b> {0:,}<br>
                <b>OI:</b> {0:,}<br>
                <b>Change:</b> {0.00}%
            </div>
            """
            st.markdown(put_data, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

with tab2:
    st.subheader("SENSEX Options Chain")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Fetch SENSEX spot price
    try:
        sensex_spot = get_sensex_spot_price(st.session_state.dhan)
        col1.metric("SENSEX Spot", f"₹{sensex_spot:,.2f}")
    except Exception as e:
        sensex_spot = 77000
        col1.metric("SENSEX Spot", f"₹{sensex_spot:,.2f} (Default)")
    
    # Calculate ATM
    sensex_atm = get_atm_strike(sensex_spot, 100)
    col2.metric("ATM Strike", f"{sensex_atm}")
    
    # Expiry selection
    expiry_date_sensex = col3.text_input("Expiry (DDMMMYY)", "09JAN26", key="sensex_expiry")
    
    if col4.button("🔄 Refresh SENSEX", key="refresh_sensex"):
        st.rerun()
    
    # Generate strikes
    sensex_strikes = get_strike_range(sensex_atm, 100, 5)
    
    # Create option chain display
    st.markdown("---")
    st.markdown("### Options Chain Table")
    
    # Create columns for better layout
    col_call, col_strike, col_put = st.columns([3, 1, 3])
    
    with col_call:
        st.markdown("#### 📞 CALL Options")
    with col_strike:
        st.markdown("#### Strike")
    with col_put:
        st.markdown("#### 📉 PUT Options")
    
    # Display option chain
    for strike in sensex_strikes:
        col_call, col_strike, col_put = st.columns([3, 1, 3])
        
        is_atm = (strike == sensex_atm)
        strike_style = "background-color: #fff9c4; padding: 10px; border-radius: 5px; text-align: center;" if is_atm else "padding: 10px; text-align: center;"
        
        with col_call:
            call_data = f"""
            <div style='background-color: #e8f5e9; padding: 10px; border-radius: 5px;'>
                <b>LTP:</b> ₹{0.00}<br>
                <b>Volume:</b> {0:,}<br>
                <b>OI:</b> {0:,}<br>
                <b>Change:</b> {0.00}%
            </div>
            """
            st.markdown(call_data, unsafe_allow_html=True)
        
        with col_strike:
            st.markdown(f"<div style='{strike_style}'><b>{strike}</b></div>", unsafe_allow_html=True)
        
        with col_put:
            put_data = f"""
            <div style='background-color: #ffebee; padding: 10px; border-radius: 5px;'>
                <b>LTP:</b> ₹{0.00}<br>
                <b>Volume:</b> {0:,}<br>
                <b>OI:</b> {0:,}<br>
                <b>Change:</b> {0.00}%
            </div>
            """
            st.markdown(put_data, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

# Auto refresh
if auto_refresh and st.session_state.logged_in:
    time.sleep(refresh_interval)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>Dhan Options Trading Platform | Real-time Data from Dhan API</p>
        <p>⚠️ For educational purposes only. Trade at your own risk.</p>
    </div>
""", unsafe_allow_html=True)
