# Dhan Options Trading Platform

A comprehensive Streamlit-based trading platform for analyzing NIFTY 50 and SENSEX options chains with real-time data from Dhan API.

## Features

✅ **Live Options Chain Data**
- Real-time NIFTY 50 and SENSEX options data
- ATM ±5 strike prices display
- Both CALL and PUT options side by side

✅ **Advanced Analytics**
- Put-Call Ratio (PCR) analysis
- Open Interest (OI) tracking
- Volume analysis
- Implied Volatility (IV) display
- Price change indicators

✅ **User-Friendly Interface**
- Clean tabular format
- ATM strike highlighting
- Color-coded price changes
- Auto-refresh capability
- Responsive design

## Installation

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Get Dhan API Credentials

1. Login to your Dhan account at https://dhan.co
2. Navigate to: **Settings → API → Generate Access Token**
3. Copy your:
   - Client ID
   - Access Token

### Step 3: Run the Application

```bash
streamlit run dhan_options_platform_live.py
```

## Usage

### Login
1. Enter your Dhan Client ID in the sidebar
2. Enter your Access Token
3. Click "Login to Dhan"

### View Options Chain

#### NIFTY 50 Tab
- Displays NIFTY spot price
- Shows ATM strike price
- Enter expiry date (format: DDMMMYY, e.g., 26JAN23)
- View options chain with:
  - Call Options (left side) - Green background
  - Strike Prices (center) - Yellow for ATM
  - Put Options (right side) - Red background

#### SENSEX Tab
- Same features as NIFTY
- SENSEX-specific data and strikes

### Understanding the Data

**Columns:**
- `C_OI`: Call Open Interest
- `C_Volume`: Call Trading Volume
- `C_IV`: Call Implied Volatility
- `C_LTP`: Call Last Traded Price
- `C_Change`: Call Price Change %
- `Strike`: Strike Price
- `P_Change`: Put Price Change %
- `P_LTP`: Put Last Traded Price
- `P_IV`: Put Implied Volatility
- `P_Volume`: Put Trading Volume
- `P_OI`: Put Open Interest

**Color Coding:**
- 🟢 Green: Positive change
- 🔴 Red: Negative change
- 🟡 Yellow: ATM strike

**PCR Analysis:**
- PCR > 1: Bearish sentiment (more puts)
- PCR < 1: Bullish sentiment (more calls)
- PCR ≈ 1: Neutral market

## File Structure

```
├── dhan_options_platform.py          # Basic version with demo data
├── dhan_options_platform_live.py     # Live version with real Dhan API
├── requirements.txt                   # Python dependencies
└── README.md                          # This file
```

## Configuration

### Settings (in sidebar)
- **Strikes to Display**: Adjust number of strikes above/below ATM (3-10)
- **Auto Refresh**: Enable/disable automatic data refresh
- **Refresh Interval**: Set refresh frequency (5-60 seconds)

## API Rate Limits

Dhan API has rate limits. The platform:
- Fetches data on-demand
- Implements error handling for failed requests
- Shows demo data when API is unavailable

## Strike Price Intervals

- **NIFTY 50**: 50 points interval
- **SENSEX**: 100 points interval

## Expiry Date Format

Use format: **DDMMMYY**
Examples:
- 26JAN23 (26th January 2023)
- 02FEB23 (2nd February 2023)
- 09MAR23 (9th March 2023)

## Security IDs (Dhan Format)

**NIFTY Format:**
- Call: `NIFTY{EXPIRY}{STRIKE}CE`
- Put: `NIFTY{EXPIRY}{STRIKE}PE`
- Example: `NIFTY26JAN2323500CE`

**SENSEX Format:**
- Call: `SENSEX{EXPIRY}{STRIKE}CE`
- Put: `SENSEX{EXPIRY}{STRIKE}PE`
- Example: `SENSEX26JAN2377000CE`

## Troubleshooting

### Login Issues
- Verify Client ID and Access Token
- Check if API access is enabled in Dhan account
- Ensure sufficient API credits

### No Data Showing
- Check expiry date format
- Verify market hours (9:15 AM - 3:30 PM IST)
- Ensure strikes are valid for current market price

### Slow Performance
- Reduce number of strikes displayed
- Increase refresh interval
- Check internet connection

## Known Limitations

1. **Market Hours**: Live data only during market hours
2. **API Limits**: Subject to Dhan API rate limits
3. **Historical Data**: Platform shows current data only
4. **Greeks**: Advanced Greeks calculations coming soon

## Disclaimer

⚠️ **IMPORTANT**: This platform is for educational and analysis purposes only.

- Not financial advice
- Trade at your own risk
- Past performance doesn't guarantee future results
- Consult a financial advisor before trading

## Support

For issues related to:
- **Dhan API**: Contact Dhan support
- **Platform bugs**: Check code and error messages
- **Feature requests**: Modify code as needed

## Future Enhancements

🚧 **Coming Soon:**
- Greeks calculations (Delta, Gamma, Theta, Vega)
- Max Pain analysis
- Historical data charts
- Strategy builder
- Alert system
- Export to CSV/Excel

## Version

**Current Version**: 1.0.0
**Last Updated**: January 2026

## License

This is a personal trading tool. Use at your own discretion.

---

**Happy Trading! 📈📊**
