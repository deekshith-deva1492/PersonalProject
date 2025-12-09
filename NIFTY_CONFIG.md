# 🇮🇳 Bot Now Configured for India NSE Trading

## ✅ Changes Summary

### 1. Risk Management Updated
- **Risk per trade:** Changed from 0.5% to **1%**
- **Max positions:** Changed from 3 to **5**
- **Max daily loss:** Changed from 2% to **3%**

### 2. Market Changed
- **Exchange:** NSE (National Stock Exchange, India)
- **Symbols:** All 50 NIFTY stocks
- **Trading hours:** 9:15 AM - 3:30 PM IST
- **Timezone:** Asia/Kolkata

### 3. Broker Integration
- **Broker:** Zerodha Kite Connect API
- **Order type:** MIS (Intraday)
- **Data source:** Zerodha historical data + yfinance backup

---

## 📋 Quick Setup Steps

### Step 1: Install Dependencies
```powershell
pip install kiteconnect
```

### Step 2: Create Zerodha Kite App
1. Go to: https://developers.kite.trade/
2. Login and create new app
3. Get your API Key and Secret

### Step 3: Create .env File
```powershell
Copy-Item .env.example .env
```

Then edit `.env` and add your credentials:
```
ZERODHA_API_KEY=your_key_here
ZERODHA_API_SECRET=your_secret_here
```

### Step 4: Generate Access Token
```powershell
python zerodha_login.py
```

### Step 5: Test Paper Trading
```powershell
python main.py --mode paper
```

---

## 📊 NIFTY 50 Stocks Configured

Your bot will scan these 50 stocks:

**Banking & Finance (15):**
- HDFCBANK, ICICIBANK, KOTAKBANK, AXISBANK, SBIN
- INDUSINDBK, BAJFINANCE, BAJAJFINSV, SBILIFE, HDFCLIFE

**IT & Technology (5):**
- TCS, INFY, WIPRO, HCLTECH, TECHM

**Consumer (8):**
- HINDUNILVR, ITC, NESTLEIND, BRITANNIA, TATACONSUM
- TITAN, MARUTI, EICHERMOT

**Energy & Resources (9):**
- RELIANCE, ONGC, NTPC, POWERGRID, COALINDIA
- BPCL, ADANIENT, ADANIPORTS, UPL

**Industrials (7):**
- LT, TATAMOTORS, TATASTEEL, M&M, BAJAJ-AUTO
- JSWSTEEL, GRASIM

**Healthcare & Pharma (5):**
- SUNPHARMA, DRREDDY, DIVISLAB, CIPLA, APOLLOHOSP

**Telecom (1):**
- BHARTIARTL

**Others (3):**
- ASIANPAINT, ULTRACEMCO, SHREECEM, HINDALCO, HEROMOTOCO

---

## 💰 Position Sizing with 1% Risk

### Example Calculation:

**Capital:** ₹1,00,000
**Risk:** 1% = ₹1,000 per trade

**Trade:** RELIANCE @ ₹2,500
**Stop loss:** 0.3% = ₹7.5 per share

**Position size:** ₹1,000 ÷ ₹7.5 = **133 shares**
**Investment:** 133 × ₹2,500 = **₹3,32,500**
**Margin (MIS 5x):** ₹3,32,500 ÷ 5 = **₹66,500 required**

---

## 📁 New Files Created

1. **`src/brokers/zerodha_broker.py`** - Zerodha API integration
2. **`zerodha_login.py`** - One-time login script
3. **`ZERODHA_SETUP.md`** - Complete setup guide
4. **`.env.example`** - Environment variables template
5. **`.gitignore`** - Security (prevents API key commits)

---

## ⚙️ Updated Configuration

### config.yaml changes:

```yaml
symbols: All 50 NIFTY stocks (RELIANCE.NS, TCS.NS, etc.)
market_open: "09:15"
market_close: "15:30"
timezone: "Asia/Kolkata"
max_portfolio_risk: 0.01  # 1% per trade
max_open_positions: 5
max_daily_loss: 0.03  # 3%
```

---

## 🚀 Next Steps

**Read the complete setup guide:**
```powershell
notepad ZERODHA_SETUP.md
```

This guide includes:
- Detailed Zerodha account setup
- API key generation
- Login flow explanation
- Testing instructions
- Trading examples
- Troubleshooting

---

**Your bot is ready for NIFTY 50 trading with 1% risk per trade!** 🇮🇳
