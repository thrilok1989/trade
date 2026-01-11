# 📊 Dhan Options Trading Platform

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)

A powerful real-time options chain analysis platform for NIFTY 50 and SENSEX, built with Streamlit and powered by Dhan API.

[![Deploy to Streamlit](https://img.shields.io/badge/Deploy%20to-Streamlit%20Cloud-FF4B4B?style=flat&logo=streamlit)](https://streamlit.io/cloud)

---

## 🚀 Features

### 📈 Real-Time Options Data
- **Live NIFTY 50** and **SENSEX** options chains
- ATM ±5 strike prices display
- Real-time spot price updates
- Both CALL and PUT options analysis

### 📊 Advanced Analytics
- **Put-Call Ratio (PCR)** analysis
- **Open Interest (OI)** tracking
- **Volume** analysis
- **Implied Volatility (IV)** monitoring
- Price change indicators with color coding

### 🎯 User-Friendly Interface
- Clean tabular format
- ATM strike highlighting
- Color-coded price movements
- Auto-refresh capability
- Mobile-responsive design
- Dark mode support

### 🔐 Secure Authentication
- Dhan API integration
- Secure credential management
- Session-based authentication

---

## 📸 Screenshots

> Add screenshots of your deployed app here:
>
> ```markdown
> ![NIFTY Options Chain](screenshots/nifty-chain.png)
> ![SENSEX Options Chain](screenshots/sensex-chain.png)
> ![PCR Analysis](screenshots/pcr-analysis.png)
> ```

---

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Dhan trading account
- Dhan API credentials

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/dhan-options-platform.git
cd dhan-options-platform
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
streamlit run dhan_options_platform_live.py
```

5. **Open browser**
- Navigate to `http://localhost:8501`

---

## ☁️ Deploy to Streamlit Cloud

### Quick Deploy

1. Fork this repository
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Sign in with GitHub
4. Click "New app"
5. Select this repository
6. Set main file: `dhan_options_platform_live.py`
7. Click "Deploy!"

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 🔑 Getting Dhan API Credentials

1. Login to your [Dhan account](https://dhan.co)
2. Navigate to **Settings → API**
3. Click **"Generate Access Token"**
4. Copy your **Client ID** and **Access Token**
5. Enter credentials in the app sidebar

---

## 📖 Usage Guide

### 1. Login
- Enter your Dhan Client ID
- Enter your Access Token
- Click "Login to Dhan"

### 2. View Options Chain

#### NIFTY 50
- View real-time spot price
- Check ATM strike
- Enter expiry date (format: `DDMMMYY`)
- Analyze options data

#### SENSEX
- Same features as NIFTY
- 100-point strike intervals

### 3. Understanding the Data

| Column | Description |
|--------|-------------|
| `C_OI` | Call Open Interest |
| `C_Volume` | Call Trading Volume |
| `C_IV` | Call Implied Volatility |
| `C_LTP` | Call Last Traded Price |
| `C_Change` | Call Price Change % |
| `Strike` | Strike Price |
| `P_Change` | Put Price Change % |
| `P_LTP` | Put Last Traded Price |
| `P_IV` | Put Implied Volatility |
| `P_Volume` | Put Trading Volume |
| `P_OI` | Put Open Interest |

### 4. PCR Analysis

- **PCR > 1**: Bearish sentiment (more puts)
- **PCR < 1**: Bullish sentiment (more calls)
- **PCR ≈ 1**: Neutral market

---

## 📂 Project Structure

```
dhan-options-platform/
├── .streamlit/
│   ├── config.toml                    # Streamlit configuration
│   └── secrets.toml.template          # Secrets template
├── dhan_options_platform_live.py      # Main application
├── requirements.txt                    # Python dependencies
├── packages.txt                        # System packages
├── .gitignore                         # Git ignore rules
├── README.md                          # This file
└── DEPLOYMENT.md                      # Deployment guide
```

---

## ⚙️ Configuration

### Streamlit Settings
Adjust in sidebar:
- **Strikes to Display**: 3-10 strikes
- **Auto Refresh**: Enable/disable
- **Refresh Interval**: 5-60 seconds

### Strike Intervals
- **NIFTY 50**: 50 points
- **SENSEX**: 100 points

### Expiry Format
Use format: `DDMMMYY`
- Example: `26JAN26`, `02FEB26`, `09MAR26`

---

## 🔧 Technical Details

### Built With
- **Streamlit** - Web framework
- **Pandas** - Data manipulation
- **DhanHQ** - API integration
- **Python 3.8+** - Programming language

### API Integration
```python
from dhanhq import dhanhq

# Initialize
dhan = dhanhq(client_id, access_token)

# Get quote
quote = dhan.get_market_quote(security_id, exchange)
```

### Data Refresh
- On-demand refresh via button
- Auto-refresh (5-60 seconds)
- Real-time updates during market hours

---

## 🐛 Troubleshooting

### Common Issues

**Login Failed**
- Verify credentials are correct
- Check API access is enabled
- Regenerate access token if expired

**No Data Showing**
- Check market hours (9:15 AM - 3:30 PM IST)
- Verify expiry date format
- Ensure strikes are valid

**Slow Performance**
- Reduce number of strikes
- Increase refresh interval
- Check internet connection

**API Rate Limits**
- Implement caching
- Reduce API calls
- Use batch requests

---

## 📊 Limitations

1. **Market Hours**: Live data only during trading hours
2. **API Limits**: Subject to Dhan API rate limits
3. **Historical Data**: Current data only
4. **Greeks**: Advanced calculations coming soon

---

## 🚀 Future Enhancements

- [ ] Greeks calculations (Delta, Gamma, Theta, Vega)
- [ ] Max Pain analysis
- [ ] Historical data charts
- [ ] Strategy builder
- [ ] Alert system (Telegram/Email)
- [ ] Export to CSV/Excel
- [ ] Multi-timeframe analysis
- [ ] Options strategies analyzer
- [ ] Backtesting engine
- [ ] Mobile app

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

**IMPORTANT**: This platform is for educational and analysis purposes only.

- Not financial advice
- Trade at your own risk
- Past performance ≠ future results
- Consult a financial advisor before trading
- Author is not responsible for trading losses

---

## 📞 Support

### For Issues
- **GitHub Issues**: [Create an issue](https://github.com/YOUR_USERNAME/dhan-options-platform/issues)
- **Discussions**: [Start a discussion](https://github.com/YOUR_USERNAME/dhan-options-platform/discussions)

### For Dhan API
- **Dhan Support**: support@dhan.co
- **API Docs**: https://api.dhan.co

---

## 🌟 Show Your Support

If you find this project useful, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs
- 💡 Suggesting new features
- 🔀 Contributing code
- 📢 Sharing with others

---

## 📚 Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [Dhan API Documentation](https://api.dhan.co)
- [Options Trading Guide](https://www.investopedia.com/options-basics-tutorial-4583012)
- [Python Pandas Tutorial](https://pandas.pydata.org/docs/user_guide/index.html)

---

## 👨‍💻 Author

**Your Name**
- GitHub: [@YOUR_USERNAME](https://github.com/YOUR_USERNAME)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)
- Twitter: [@yourhandle](https://twitter.com/yourhandle)

---

## 🎉 Acknowledgments

- Thanks to Dhan for providing the API
- Streamlit for the amazing framework
- Python community for excellent libraries
- All contributors and users

---

## 📈 Stats

![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/dhan-options-platform?style=social)
![GitHub forks](https://img.shields.io/github/forks/YOUR_USERNAME/dhan-options-platform?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/YOUR_USERNAME/dhan-options-platform?style=social)

---

**Made with ❤️ by traders, for traders**

**Happy Trading! 📈📊**

---

<div align="center">
  
### ⭐ Star this repo if you find it helpful! ⭐

</div>
