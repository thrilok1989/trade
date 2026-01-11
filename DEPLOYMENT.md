# 🚀 Deployment Guide - GitHub + Streamlit Cloud

Complete step-by-step guide to deploy your Dhan Options Trading Platform on Streamlit Cloud.

---

## 📋 Prerequisites

- GitHub account
- Streamlit Cloud account (free at https://streamlit.io/cloud)
- Dhan trading account with API access
- Git installed on your computer

---

## 🔧 Step 1: Prepare Your Repository

### 1.1 Create Local Repository

```bash
# Create a new directory
mkdir dhan-options-platform
cd dhan-options-platform

# Initialize git
git init

# Copy all files to this directory
# - dhan_options_platform_live.py
# - requirements.txt
# - README.md
# - .gitignore
# - packages.txt
# - .streamlit/config.toml
# - .streamlit/secrets.toml.template
```

### 1.2 File Structure

Your repository should look like this:

```
dhan-options-platform/
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.template
├── .gitignore
├── dhan_options_platform_live.py
├── requirements.txt
├── packages.txt
├── README.md
└── DEPLOYMENT.md (this file)
```

---

## 📤 Step 2: Push to GitHub

### 2.1 Create GitHub Repository

1. Go to https://github.com
2. Click "New repository"
3. Repository name: `dhan-options-platform`
4. Description: "Live NIFTY & SENSEX Options Chain Analysis Platform"
5. Keep it **Public** (required for free Streamlit Cloud)
6. Don't initialize with README (we already have one)
7. Click "Create repository"

### 2.2 Push Your Code

```bash
# Add all files
git add .

# Commit
git commit -m "Initial commit: Dhan Options Trading Platform"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/dhan-options-platform.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## ☁️ Step 3: Deploy on Streamlit Cloud

### 3.1 Connect to Streamlit Cloud

1. Go to https://streamlit.io/cloud
2. Sign in with GitHub
3. Click "New app"

### 3.2 Configure Deployment

Fill in the deployment form:

- **Repository**: `YOUR_USERNAME/dhan-options-platform`
- **Branch**: `main`
- **Main file path**: `dhan_options_platform_live.py`
- **App URL**: Choose a custom URL (e.g., `your-dhan-platform`)

### 3.3 Add Secrets (Optional)

If you want to pre-configure API credentials:

1. Click "Advanced settings"
2. In "Secrets" section, add:

```toml
[dhan]
client_id = "your_client_id_here"
access_token = "your_access_token_here"
```

⚠️ **Note**: Users can also enter credentials via the UI, so this is optional.

### 3.4 Deploy

1. Click "Deploy!"
2. Wait 2-3 minutes for deployment
3. Your app will be live at: `https://your-dhan-platform.streamlit.app`

---

## 🔐 Step 4: Get Dhan API Credentials

### 4.1 Login to Dhan

1. Go to https://dhan.co
2. Login to your account

### 4.2 Generate API Token

1. Navigate to: **Settings → API**
2. Click "Generate Access Token"
3. Copy your:
   - **Client ID**
   - **Access Token**

### 4.3 Save Credentials Securely

**Option A: Enter via UI** (Recommended)
- Open your deployed app
- Enter credentials in the sidebar
- Login to start using

**Option B: Use Streamlit Secrets**
- Add to Streamlit Cloud secrets (Step 3.3)
- Modify code to read from secrets

---

## 🔄 Step 5: Update and Maintain

### 5.1 Update Code

```bash
# Make changes to your files
# Then commit and push

git add .
git commit -m "Description of changes"
git push origin main
```

Streamlit Cloud will **automatically redeploy** when you push changes!

### 5.2 Check Logs

1. Go to Streamlit Cloud dashboard
2. Click on your app
3. View logs in the bottom panel
4. Debug any issues

---

## 🎯 Quick Reference

### Important URLs

- **GitHub Repo**: `https://github.com/YOUR_USERNAME/dhan-options-platform`
- **Streamlit App**: `https://your-dhan-platform.streamlit.app`
- **Streamlit Dashboard**: `https://share.streamlit.io`
- **Dhan API Docs**: `https://api.dhan.co`

### Common Commands

```bash
# Check status
git status

# Pull latest changes
git pull origin main

# Push updates
git add .
git commit -m "Update message"
git push origin main

# View remote
git remote -v
```

---

## 🐛 Troubleshooting

### Issue: "Module not found"

**Solution**: Check `requirements.txt` has all dependencies

```txt
streamlit==1.31.0
dhanhq==1.3.3
pandas==2.1.4
```

### Issue: "API authentication failed"

**Solutions**:
1. Verify Client ID and Access Token are correct
2. Check if API access is enabled in Dhan account
3. Regenerate Access Token if expired

### Issue: "App not loading"

**Solutions**:
1. Check Streamlit Cloud logs
2. Verify main file path is correct: `dhan_options_platform_live.py`
3. Ensure branch is set to `main`

### Issue: "No data showing"

**Solutions**:
1. Check market hours (9:15 AM - 3:30 PM IST)
2. Verify expiry date format (DDMMMYY)
3. Check if strikes are valid

---

## 📊 Monitoring Usage

### Streamlit Cloud Limits (Free Tier)

- **1 private app** or unlimited public apps
- **1 GB RAM**
- **1 CPU core**
- **Unlimited viewers**

If you need more resources, consider upgrading to paid plans.

### Check App Performance

1. Monitor response times
2. Check error logs regularly
3. Optimize code if slow
4. Reduce API calls if hitting limits

---

## 🔒 Security Best Practices

### ✅ DO:
- Keep repository public for free Streamlit Cloud
- Use Streamlit secrets for API keys
- Add `.gitignore` to exclude sensitive files
- Regularly update dependencies
- Monitor for security vulnerabilities

### ❌ DON'T:
- Commit API keys to GitHub
- Share access tokens publicly
- Hardcode credentials in code
- Ignore security warnings

---

## 🎓 Additional Resources

### Documentation

- [Streamlit Docs](https://docs.streamlit.io)
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Dhan API Docs](https://api.dhan.co)
- [Git Basics](https://git-scm.com/book/en/v2)

### Video Tutorials

- [Deploying Streamlit Apps](https://www.youtube.com/streamlit)
- [Git & GitHub Tutorial](https://www.youtube.com/watch?v=RGOj5yH7evk)

---

## 💡 Pro Tips

1. **Use GitHub Issues** to track bugs and features
2. **Create branches** for testing new features
3. **Add a LICENSE** file (MIT recommended)
4. **Write good commit messages**
5. **Keep README updated** with new features
6. **Add screenshots** to README for better visibility
7. **Tag releases** for version control

---

## 📞 Support

### For Deployment Issues:
- Streamlit Community Forum: https://discuss.streamlit.io
- GitHub Issues: Create issue in your repo

### For API Issues:
- Dhan Support: support@dhan.co
- Dhan API Documentation: https://api.dhan.co

### For Code Issues:
- Check error logs in Streamlit Cloud
- Debug locally first: `streamlit run dhan_options_platform_live.py`
- Review code and fix bugs

---

## ✨ Next Steps After Deployment

1. **Share your app** with other traders
2. **Gather feedback** from users
3. **Add new features** (Greeks, alerts, etc.)
4. **Monitor performance** and optimize
5. **Update regularly** with market changes

---

## 🎉 Congratulations!

Your Dhan Options Trading Platform is now live! 

Share it with the community and happy trading! 📈📊

---

**Last Updated**: January 2026  
**Version**: 1.0.0
