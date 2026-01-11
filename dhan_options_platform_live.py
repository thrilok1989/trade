import streamlit as st
import pandas as pd
from dhanhq import dhanhq, marketfeed
import time
from datetime import datetime, timedelta
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
    .main {
        padding: 0rem 1rem;
    }
    .dataframe {
        font-size: 12px;
    }
    .atm-row {
        background-color: #fff9c4 !important;
        font-weight: bold !important;
    }
    .call-positive {
        color: #2e7d32;
    }
    .call-negative {
        color: #c62828;
    }
    .put-positive {
        color: #c62828;
    }
    .put-negative {
        color: #2e7d32;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'dhan' not in st.session_state:
    st.session_state.dhan = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'last_update' not in st.session_state:
    st.session_state.last_update = None

# Security IDs for indices
NIFTY_SECURITY_ID = "13"
SENSEX_SECURITY_ID = "51"

# Sidebar
with st.sidebar:
    st.title("🔐 Dhan Login")
    
    if not st.session_state.logged_in:
        client_id = st.text_input("Client ID", type="password", key="client_id")
        access_token = st.text_input("Access Token", type="password", key="access_token")
        
        if st.button("Login to Dhan"):
            if client_id and access_token:
                try:
                    dhan = dhanhq(client_id, access_token)
                    # Test connection
                    dhan.get_fund_limits()
                    st.session_state.dhan = dhan
                    st.session_state.logged_in = True
                    st.success("✅ Login successful!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Login failed: {str(e)}")
            else:
                st.warning("Enter credentials")
    else:
        st.success("✅ Connected to Dhan")
        
        if st.button("Logout"):
            st.session_state.dhan = None
            st.session_state.logged_in = False
            st.rerun()
        
        st.divider()
        
        # Settings
        st.markdown("### ⚙️ Settings")
        num_strikes = st.slider("Strikes to Display", 3, 10, 5)
        
        st.divider()
        
        # Account info
        try:
            funds = st.session_state.dhan.get_fund_limits()
            available = funds.get('data', {}).get('availabelBalance', 0)
            st.metric("Available Balance", f"₹{available:,.2f}")
        except:
            pass

# Main content
st.title("📊 Dhan Options Trading Platform")

if not st.session_state.logged_in:
    st.warning("⚠️ Please login to access live options data")
    
    st.markdown("""
    ### How to get Dhan API credentials:
    1. Login to your Dhan account
    2. Go to Settings → API → Generate Access Token
    3. Copy your Client ID and Access Token
    4. Enter them in the sidebar
    """)
    st.stop()

# Helper functions
def get_spot_price(dhan, security_id, exchange):
    """Fetch spot price for index"""
    try:
        quote = dhan.get_market_quote(security_id, exchange)
        if quote and 'data' in quote:
            ltp = quote['data'].get('LTP', 0)
            return ltp
        return 0
    except Exception as e:
        st.error(f"Error fetching spot price: {str(e)}")
        return 0

def get_atm_strike(spot_price, strike_diff):
    """Calculate ATM strike"""
    return round(spot_price / strike_diff) * strike_diff

def get_strikes_list(atm, strike_diff, num_strikes):
    """Generate strike list"""
    strikes = []
    for i in range(-num_strikes, num_strikes + 1):
        strikes.append(atm + (i * strike_diff))
    return strikes

def fetch_options_data(dhan, symbol, strikes, expiry, option_type, exchange):
    """Fetch option chain data"""
    options_data = []
    
    for strike in strikes:
        try:
            # Build security ID based on Dhan format
            # Example: NIFTY26JAN2325000CE for NIFTY Call
            if symbol == "NIFTY":
                sec_id = f"NIFTY{expiry}{strike}{option_type}"
            else:  # SENSEX
                sec_id = f"SENSEX{expiry}{strike}{option_type}"
            
            # Fetch quote
            quote = dhan.get_market_quote(sec_id, exchange)
            
            if quote and 'data' in quote:
                data = quote['data']
                options_data.append({
                    'strike': strike,
                    'ltp': data.get('LTP', 0),
                    'volume': data.get('volume', 0),
                    'oi': data.get('OI', 0),
                    'change': data.get('change', 0),
                    'bid': data.get('bidPrice', 0),
                    'ask': data.get('askPrice', 0),
                    'iv': data.get('IV', 0)
                })
            else:
                options_data.append({
                    'strike': strike,
                    'ltp': 0,
                    'volume': 0,
                    'oi': 0,
                    'change': 0,
                    'bid': 0,
                    'ask': 0,
                    'iv': 0
                })
        except Exception as e:
            # Add placeholder data if fetch fails
            options_data.append({
                'strike': strike,
                'ltp': 0,
                'volume': 0,
                'oi': 0,
                'change': 0,
                'bid': 0,
                'ask': 0,
                'iv': 0
            })
    
    return options_data

def create_options_chain_df(call_data, put_data, strikes):
    """Create combined options chain dataframe"""
    df_data = []
    
    for i, strike in enumerate(strikes):
        call = call_data[i] if i < len(call_data) else {}
        put = put_data[i] if i < len(put_data) else {}
        
        df_data.append({
            'C_OI': call.get('oi', 0),
            'C_Volume': call.get('volume', 0),
            'C_IV': call.get('iv', 0),
            'C_LTP': call.get('ltp', 0),
            'C_Change': call.get('change', 0),
            'Strike': strike,
            'P_Change': put.get('change', 0),
            'P_LTP': put.get('ltp', 0),
            'P_IV': put.get('iv', 0),
            'P_Volume': put.get('volume', 0),
            'P_OI': put.get('oi', 0),
        })
    
    return pd.DataFrame(df_data)

def style_dataframe(df, atm_strike):
    """Apply styling to dataframe"""
    def highlight_atm(row):
        if row['Strike'] == atm_strike:
            return ['background-color: #fff9c4; font-weight: bold'] * len(row)
        return [''] * len(row)
    
    def color_change(val):
        if isinstance(val, (int, float)):
            if val > 0:
                return 'color: #2e7d32'
            elif val < 0:
                return 'color: #c62828'
        return ''
    
    styled = df.style.apply(highlight_atm, axis=1)
    styled = styled.applymap(color_change, subset=['C_Change', 'P_Change'])
    
    return styled

# Main content
st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Create tabs
tab1, tab2, tab3 = st.tabs(["📈 NIFTY 50", "📊 SENSEX", "📉 Greeks Analysis"])

with tab1:
    st.subheader("NIFTY 50 Options Chain")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Fetch NIFTY spot
    nifty_spot = get_spot_price(st.session_state.dhan, NIFTY_SECURITY_ID, "IDX_I")
    
    if nifty_spot == 0:
        nifty_spot = 23500  # Fallback
        col1.metric("NIFTY Spot", f"₹{nifty_spot:,.2f}", "Demo Mode")
    else:
        col1.metric("NIFTY Spot", f"₹{nifty_spot:,.2f}")
    
    # ATM calculation
    nifty_atm = get_atm_strike(nifty_spot, 50)
    col2.metric("ATM Strike", nifty_atm)
    
    # Expiry input
    expiry_nifty = col3.text_input("Expiry", "26JAN23", key="nifty_exp")
    
    # Refresh button
    if col4.button("🔄 Refresh", key="refresh_nifty"):
        st.rerun()
    
    # Generate strikes
    nifty_strikes = get_strikes_list(nifty_atm, 50, num_strikes)
    
    st.markdown("---")
    
    # Fetch data
    with st.spinner("Fetching NIFTY options data..."):
        call_data = fetch_options_data(
            st.session_state.dhan, 
            "NIFTY", 
            nifty_strikes, 
            expiry_nifty, 
            "CE", 
            "NSE_FNO"
        )
        
        put_data = fetch_options_data(
            st.session_state.dhan, 
            "NIFTY", 
            nifty_strikes, 
            expiry_nifty, 
            "PE", 
            "NSE_FNO"
        )
    
    # Create dataframe
    nifty_df = create_options_chain_df(call_data, put_data, nifty_strikes)
    
    # Display
    st.dataframe(
        style_dataframe(nifty_df, nifty_atm),
        use_container_width=True,
        height=600
    )
    
    # PCR Analysis
    col1, col2, col3 = st.columns(3)
    total_call_oi = nifty_df['C_OI'].sum()
    total_put_oi = nifty_df['P_OI'].sum()
    pcr = total_put_oi / total_call_oi if total_call_oi > 0 else 0
    
    col1.metric("Total Call OI", f"{total_call_oi:,.0f}")
    col2.metric("Total Put OI", f"{total_put_oi:,.0f}")
    col3.metric("PCR Ratio", f"{pcr:.2f}")

with tab2:
    st.subheader("SENSEX Options Chain")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Fetch SENSEX spot
    sensex_spot = get_spot_price(st.session_state.dhan, SENSEX_SECURITY_ID, "BSE_IDX")
    
    if sensex_spot == 0:
        sensex_spot = 77000  # Fallback
        col1.metric("SENSEX Spot", f"₹{sensex_spot:,.2f}", "Demo Mode")
    else:
        col1.metric("SENSEX Spot", f"₹{sensex_spot:,.2f}")
    
    # ATM calculation
    sensex_atm = get_atm_strike(sensex_spot, 100)
    col2.metric("ATM Strike", sensex_atm)
    
    # Expiry input
    expiry_sensex = col3.text_input("Expiry", "26JAN23", key="sensex_exp")
    
    # Refresh button
    if col4.button("🔄 Refresh", key="refresh_sensex"):
        st.rerun()
    
    # Generate strikes
    sensex_strikes = get_strikes_list(sensex_atm, 100, num_strikes)
    
    st.markdown("---")
    
    # Fetch data
    with st.spinner("Fetching SENSEX options data..."):
        call_data = fetch_options_data(
            st.session_state.dhan, 
            "SENSEX", 
            sensex_strikes, 
            expiry_sensex, 
            "CE", 
            "BSE_FNO"
        )
        
        put_data = fetch_options_data(
            st.session_state.dhan, 
            "SENSEX", 
            sensex_strikes, 
            expiry_sensex, 
            "PE", 
            "BSE_FNO"
        )
    
    # Create dataframe
    sensex_df = create_options_chain_df(call_data, put_data, sensex_strikes)
    
    # Display
    st.dataframe(
        style_dataframe(sensex_df, sensex_atm),
        use_container_width=True,
        height=600
    )
    
    # PCR Analysis
    col1, col2, col3 = st.columns(3)
    total_call_oi = sensex_df['C_OI'].sum()
    total_put_oi = sensex_df['P_OI'].sum()
    pcr = total_put_oi / total_call_oi if total_call_oi > 0 else 0
    
    col1.metric("Total Call OI", f"{total_call_oi:,.0f}")
    col2.metric("Total Put OI", f"{total_put_oi:,.0f}")
    col3.metric("PCR Ratio", f"{pcr:.2f}")

with tab3:
    st.subheader("Greeks Analysis")
    st.info("🚧 Greeks analysis coming soon! This will include Delta, Gamma, Theta, Vega calculations.")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray; font-size: 12px;'>
        <p>📊 Dhan Options Trading Platform | Powered by Dhan API</p>
        <p>⚠️ For educational and analysis purposes only. Trade at your own risk.</p>
    </div>
""", unsafe_allow_html=True)
