# 🔔 Alert System Guide

Your trading bot now has **multiple alert mechanisms** to notify you when signals are found!

## ✅ Already Working (No Setup Required)

### 1. **Desktop Notifications** 🖥️
- Pop-up notifications on your Windows desktop
- Shows signal details (symbol, price, type)
- Appears automatically when signal found
- **Status**: ✅ READY TO USE

### 2. **Sound Alerts** 🔊
- Different beeps for BUY vs SELL signals
- BUY: Higher pitch (1000-1200 Hz)
- SELL: Lower pitch (600-800 Hz)
- Multiple signals: Triple beep
- **Status**: ✅ READY TO USE

---

## 🎯 How to Use Alerts

### Scanner Dashboard (Recommended)
1. Open scanner dashboard: http://localhost:8505
2. In sidebar, you'll see **"🔔 Alert Settings"**
3. Toggle options:
   - ✅ Desktop Notifications (enabled by default)
   - ✅ Sound Alerts (enabled by default)
4. Click **"🧪 Test Alerts"** to test notifications
5. Enable **"Auto-Scan"** to scan continuously

### What Happens When Signal Found:
- 🖥️ **Desktop popup** shows signal details
- 🔊 **Sound beep** plays (different for BUY/SELL)
- 📊 **Dashboard updates** with new signal
- ✅ You get notified **instantly**!

---

## 📧 Optional: Email Alerts (Advanced)

Want email notifications? Add to your `.env` file:

```env
# Email Alert Settings
ALERT_EMAIL_FROM=your-email@gmail.com
ALERT_EMAIL_TO=your-email@gmail.com
ALERT_EMAIL_PASSWORD=your-app-password
ALERT_SMTP_SERVER=smtp.gmail.com
ALERT_SMTP_PORT=587
```

**Gmail Setup:**
1. Go to Google Account settings
2. Enable 2-Step Verification
3. Generate App Password: https://myaccount.google.com/apppasswords
4. Use that password in `ALERT_EMAIL_PASSWORD`

Then in scanner dashboard, email alerts will be available!

---

## 📱 Optional: Telegram Alerts (Advanced)

Want Telegram notifications? Follow these steps:

### Step 1: Create Telegram Bot
1. Open Telegram, search for **@BotFather**
2. Send `/newbot` and follow instructions
3. Copy the **bot token** (looks like: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### Step 2: Get Your Chat ID
1. Start a chat with your new bot
2. Send any message to it
3. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Look for `"chat":{"id":123456789}` - that's your chat ID

### Step 3: Add to .env
```env
# Telegram Alert Settings
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=123456789
```

Then in scanner dashboard, Telegram alerts will be available!

---

## 🧪 Testing Your Alerts

### Quick Test in Dashboard:
1. Open http://localhost:8505
2. Go to sidebar → "🔔 Alert Settings"
3. Click **"🧪 Test Alerts"**
4. You should see:
   - Desktop notification pop up
   - Hear a beep sound
   - (If configured) Email received
   - (If configured) Telegram message

### Test with Real Scan:
1. Click **"🔍 Scan All Symbols"**
2. If signals found, you'll get all enabled alerts automatically
3. Enable **"Auto-Scan"** for continuous monitoring

---

## 🎨 Alert Customization

You can customize alert behavior in the code:

**File**: `src/utils/alerting.py`

**Customize Sound:**
```python
# Change frequency and duration
winsound.Beep(1000, 300)  # frequency_hz, duration_ms
```

**Customize Notification Duration:**
```python
notification.notify(
    title=title,
    message=message,
    timeout=10  # seconds to show
)
```

---

## 💡 Pro Tips

1. **Leave Dashboard Open**: Keep scanner dashboard running in browser
2. **Enable Auto-Scan**: Let it scan every 60 seconds automatically
3. **Sound Alerts**: Make sure your speakers are on!
4. **Desktop Notifications**: Keep Windows notifications enabled
5. **Test First**: Use "Test Alerts" button to verify everything works
6. **Multiple Monitors**: Dashboard on one screen, work on another

---

## 🔧 Troubleshooting

### No Desktop Notifications?
- Check Windows notification settings
- Ensure plyer is installed: `pip install plyer`
- Try restarting the dashboard

### No Sound?
- Check speaker volume
- Windows only feature (winsound)
- Try the test button first

### Emails Not Working?
- Check Gmail app password
- Verify .env file settings
- Check spam folder
- Try test alerts button

### Telegram Not Working?
- Verify bot token is correct
- Ensure you messaged the bot first
- Check chat ID is correct
- Try test alerts button

---

## 📊 Alert Best Practices

**During Market Hours (9:15 AM - 3:30 PM IST):**
- Keep desktop notifications ON
- Keep sound alerts ON
- Enable auto-scan for continuous monitoring
- Dashboard in background, you'll hear alerts

**After Market Hours:**
- Disable alerts or close dashboard
- No need to keep running (market closed)

**For Multiple Signals:**
- Single signal = One notification
- Multiple signals = Summary notification showing count

---

## 🚀 Quick Start Guide

```powershell
# 1. Start scanner dashboard
python run_scanner_dashboard.py

# 2. Open in browser
# http://localhost:8505

# 3. In sidebar:
#    - Enable "Desktop Notifications" ✅
#    - Enable "Sound Alerts" ✅
#    - Click "Test Alerts" to verify 🧪
#    - Enable "Auto-Scan" for continuous monitoring

# 4. Minimize browser, continue working
#    You'll get notified when signals appear!
```

---

## 🎯 You're All Set!

Your bot will now:
- ✅ Scan all 50 NIFTY stocks continuously
- ✅ Alert you instantly when signals found
- ✅ Show desktop notifications
- ✅ Play sound alerts
- ✅ Display signals in dashboard

**No more watching the screen all day!** 🎉

Just enable auto-scan and let the bot watch the market for you!
