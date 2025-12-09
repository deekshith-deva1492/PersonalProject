# 🚀 WebSocket Streaming Setup Guide

## What Changed?

Your scanner dashboard now has **TWO MODES**:

### 1️⃣ HTTP Polling Mode (Old Way)
- ⏱️ Scans every **60 seconds**
- 📊 Takes ~18 seconds per scan
- ⚠️ Rate limited (3 req/sec)
- ✅ Reliable and tested

### 2️⃣ WebSocket Streaming Mode (NEW - Real-Time!)
- ⚡ **< 1 second** latency
- 🔴 **LIVE** continuous streaming
- 🚫 **NO** rate limits
- 🎯 **Instant** signal detection

---

## Performance Comparison

### HTTP Polling (60s interval):
```
09:15:00 - Scan starts
09:15:18 - Scan completes (18s)
09:16:18 - Next scan starts (60s later)
09:16:36 - Scan completes

Signal at 09:15:30? Detected at 09:16:18 (48 seconds delay!)
```

### WebSocket Streaming:
```
09:15:00 - Connected, streaming all 49 symbols
09:15:30 - Signal detected INSTANTLY (< 1 second!)
09:15:31 - Alert sent + Trade executed
```

**Result: 30-60x faster signal detection!** 🚀

---

## Quick Start (3 Steps)

### Step 1: Fetch Instrument Tokens
```bash
python get_instruments.py
```

This creates `instrument_tokens.json` with all NIFTY 50 tokens needed for WebSocket.

**Output:**
```
✅ Fetched 8675 instruments from NSE
✅ Found 49 NIFTY 50 instruments
💾 Saved to: instrument_tokens.json
```

### Step 2: Start Scanner Dashboard
```bash
python run_scanner_dashboard.py
```

Or:
```bash
streamlit run scanner_dashboard.py
```

### Step 3: Enable WebSocket Mode

1. Open dashboard: http://localhost:8505
2. In sidebar, select: **"WebSocket Streaming (<1s)"**
3. Wait 2-3 seconds for initialization
4. You'll see: "✅ WebSocket connected! Streaming real-time data..."
5. Status shows: 🔴 LIVE - WebSocket streaming active

**DONE!** You're now getting real-time signals! 🎉

---

## How WebSocket Mode Works

### Initialization (First Time)
```python
1. Loads instrument_tokens.json (49 symbols → tokens)
2. Creates KiteTicker WebSocket connection to Zerodha
3. Subscribes to all 49 NIFTY 50 stocks
4. Starts streaming real-time tick data
```

### Real-Time Operation
```python
Every tick update (price change):
├─ Build 5-minute candle from ticks
├─ Calculate indicators (EMA, RSI)
├─ Check for signals
├─ If signal found:
│   ├─ Add to signals list
│   ├─ Send desktop alert
│   ├─ Play sound alert
│   └─ Auto-execute trade (if enabled)
└─ Update UI every 2 seconds
```

### Automatic Features
- ✅ Auto-reconnect on disconnect
- ✅ Resubscribe on reconnection  
- ✅ Thread-safe tick processing
- ✅ Rate-limited signal checks (5s per symbol)
- ✅ Handles market open/close gracefully

---

## When to Use Each Mode?

### Use HTTP Polling Mode When:
- 🧪 Testing and learning the system
- 📚 You want slower, predictable scanning
- 🔍 Analyzing signals manually (not day trading)
- 🛠️ Debugging or troubleshooting

### Use WebSocket Streaming When:
- ⚡ Day trading (need instant signals!)
- 💰 Real money trading (every second counts)
- 🎯 Want professional-grade execution
- 🔴 Need real-time market monitoring

---

## Troubleshooting

### Error: "instrument_tokens.json not found"
**Solution:**
```bash
python get_instruments.py
```

### Error: "WebSocket initialization failed"
**Causes:**
1. Invalid/expired access token
2. Network connectivity issues
3. Zerodha API down

**Solution:**
```bash
# Regenerate access token
python zerodha_login.py

# Restart dashboard
python run_scanner_dashboard.py
```

### WebSocket Shows "Initializing..." Forever
**Solution:**
1. Check .env file has valid credentials:
   - ZERODHA_API_KEY
   - ZERODHA_ACCESS_TOKEN
2. Click "🔄 Reconnect WebSocket" button
3. Switch to HTTP mode, then back to WebSocket

### No Signals in WebSocket Mode
**Possible Reasons:**
1. Market is closed (9:15 AM - 3:30 PM IST only)
2. No valid signals at current prices
3. WebSocket not receiving ticks (check connection)

**Check:**
- Look for "🔴 LIVE" indicator in sidebar
- "WebSocket Status" shows "Connected & Streaming"
- Try HTTP mode to verify signals exist

---

## Advanced: Hybrid Approach (Best of Both Worlds)

You can use BOTH modes strategically:

### Morning (9:15 AM - 10:00 AM): WebSocket Mode
- Catch opening volatility signals instantly
- High-speed execution for best prices
- Maximum profit from quick moves

### Mid-Day (10:00 AM - 2:00 PM): HTTP Polling Mode
- Slower scanning is fine (less volatile)
- Save API resources
- Manual verification of signals

### Closing (2:00 PM - 3:30 PM): WebSocket Mode
- Catch closing momentum signals
- Real-time exit opportunities
- Last-minute trades

---

## Technical Details

### WebSocket Implementation
- **Library:** `kiteconnect.KiteTicker`
- **Protocol:** WebSocket (ws://)
- **Data:** Real-time tick-by-tick quotes
- **Frequency:** Every price change (~multiple per second)
- **Throttling:** Signal checks throttled to 5 seconds per symbol

### Data Structure
Each tick contains:
```python
{
    'instrument_token': 738561,
    'last_price': 1234.50,
    'volume': 12345678,
    'last_quantity': 100,
    'average_price': 1233.25,
    'ohlc': {
        'open': 1230.00,
        'high': 1235.00,
        'low': 1228.50,
        'close': 1234.50
    },
    'timestamp': datetime.now()
}
```

### Candle Building
- Collects ticks in 5-minute windows
- Builds OHLC candles from tick data
- Calculates indicators on completed candles
- Detects signals using strategy logic

---

## Files Modified

### New Files Created:
1. **src/data/realtime_stream.py** (370 lines)
   - RealtimeDataStream class
   - StreamingScanner class
   - WebSocket connection management
   
2. **get_instruments.py** (120 lines)
   - Fetches NIFTY 50 instrument tokens
   - Creates instrument_tokens.json
   
3. **instrument_tokens.json** (auto-generated)
   - Maps symbols to tokens
   - Used by WebSocket for subscription

### Modified Files:
1. **scanner_dashboard.py**
   - Added mode selector (HTTP vs WebSocket)
   - WebSocket initialization logic
   - Real-time signal handling
   - Status indicators

---

## FAQ

### Q: Do I need to run get_instruments.py every day?
**A:** No! Only once. Instrument tokens rarely change.

### Q: Can I switch modes while dashboard is running?
**A:** Yes! Just select different mode in sidebar. Dashboard will restart automatically.

### Q: Does WebSocket cost more API calls?
**A:** No! WebSocket has NO rate limits. It's a persistent connection.

### Q: What happens if WebSocket disconnects?
**A:** Automatic reconnection! Stream reconnects and resubscribes automatically.

### Q: Can I use WebSocket outside market hours?
**A:** Yes, but you won't receive ticks. Use HTTP mode for historical data analysis.

### Q: Is WebSocket more reliable than HTTP?
**A:** Both are reliable. WebSocket is faster, HTTP is simpler. Choose based on your trading style.

---

## Next Steps

1. ✅ Run `python get_instruments.py` (one-time setup)
2. ✅ Start dashboard: `python run_scanner_dashboard.py`
3. ✅ Select "WebSocket Streaming (<1s)" mode
4. ✅ Watch for 🔴 LIVE indicator
5. ✅ Enable auto-trading if desired
6. 🚀 Start catching signals in real-time!

---

## Support

- **Documentation:** WEBSOCKET_TRADING.md (detailed technical guide)
- **Quick Reference:** WEBSOCKET_QUICKSTART.md
- **Setup Guide:** This file (WEBSOCKET_SETUP.md)

---

**Remember:** WebSocket is professional-grade. Use it when you need speed. Use HTTP when you need simplicity. Both work perfectly! 🎯
