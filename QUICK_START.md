# 🚀 Quick Start Guide

Get your Dhan Options Platform running in **5 minutes**!

---

## ⚡ For Streamlit Cloud Deployment (Recommended)

### Step 1: Fork/Upload to GitHub (2 minutes)

1. Create a new repository on GitHub
2. Upload all files:
   - `dhan_options_platform_live.py`
   - `requirements.txt`
   - `packages.txt`
   - `.streamlit/config.toml`
   - `README.md`

### Step 2: Deploy on Streamlit Cloud (2 minutes)

1. Go to https://streamlit.io/cloud
2. Click **"New app"**
3. Select your repository
4. Main file: `dhan_options_platform_live.py`
5. Click **"Deploy"**

### Step 3: Get Dhan Credentials (1 minute)

1. Login to https://dhan.co
2. Go to **Settings → API**
3. Click **"Generate Access Token"**
4. Copy Client ID and Access Token

### Step 4: Use the App

1. Open your deployed app
2. Enter credentials in sidebar
3. Start analyzing! 📈

---

## 💻 For Local Development

### Windows Users

```bash
# 1. Double-click setup.bat
setup.bat

# 2. Run the app
streamlit run dhan_options_platform_live.py
```

### Mac/Linux Users

```bash
# 1. Run setup script
chmod +x setup.sh
./setup.sh

# 2. Run the app
streamlit run dhan_options_platform_live.py
```

### Manual Setup

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run app
streamlit run dhan_options_platform_live.py
```

---

## 📱 Using the Platform

### 1. Login
- Enter Dhan Client ID
- Enter Access Token
- Click "Login to Dhan"

### 2. View Data
- Switch between NIFTY/SENSEX tabs
- Enter expiry date (format: `26JAN26`)
- Click Refresh for latest data

### 3. Analyze
- Check PCR ratio
- Monitor OI changes
- Track volume
- Analyze IV

---

## 🔑 Dhan API Credentials

### Where to Find:
1. Login to Dhan → https://dhan.co
2. Settings → API
3. Generate Access Token

### What You Need:
- **Client ID**: Your unique identifier
- **Access Token**: Your API key

### Security:
- Never share your credentials
- Use Streamlit secrets for cloud deployment
- Regenerate if compromised

---

## 🎯 Expiry Date Format

**Format**: `DDMMMYY`

**Examples**:
- `26JAN26` = 26th January 2026
- `02FEB26` = 2nd February 2026
- `30MAR26` = 30th March 2026

---

## 📊 Understanding PCR

**Put-Call Ratio** shows market sentiment:

- **PCR > 1.2**: Strong Bearish 🔴
- **PCR 1.0-1.2**: Bearish 🟠
- **PCR 0.8-1.0**: Neutral 🟡
- **PCR 0.6-0.8**: Bullish 🟢
- **PCR < 0.6**: Strong Bullish 🟢🟢

---

## ⚡ Pro Tips

1. **Market Hours**: Use during 9:15 AM - 3:30 PM IST for live data
2. **ATM Strike**: Yellow highlighted row is ATM
3. **Color Code**: Green = Calls, Red = Puts
4. **Refresh**: Click refresh or enable auto-refresh
5. **PCR Analysis**: Check total OI for market bias

---

## 🐛 Quick Fixes

### App Not Loading?
- Check internet connection
- Verify Streamlit Cloud status
- Clear browser cache

### No Data?
- Check market hours
- Verify expiry format
- Ensure valid strikes

### Login Failed?
- Check credentials
- Regenerate access token
- Enable API in Dhan account

---

## 📞 Need Help?

- **GitHub Issues**: Report bugs
- **Dhan Support**: support@dhan.co
- **Documentation**: See README.md

---

## 🎉 That's It!

You're ready to analyze options! Happy trading! 📈📊

---

**Total Time**: ~5 minutes  
**Difficulty**: Easy  
**Cost**: Free
