# HTTP Polling Mode (Fallback Only)

## ⚠️ This mode is now DEPRECATED - Use WebSocket Streaming instead

### Why HTTP Polling is Now Fallback Only

**WebSocket Streaming** is now the default because:
- ✅ Real-time updates (< 1 second latency)
- ✅ No rate limit issues
- ✅ Continuous data stream
- ✅ Better for fast-moving markets
- ✅ Lower API call count

**HTTP Polling** should only be used:
- ⚠️ If WebSocket connection fails
- ⚠️ For debugging/testing purposes
- ⚠️ When WebSocket is not available

---

## Configuration Changes

### scanner_dashboard.py

#### Previous (HTTP was default):
```python
st.session_state.scan_mode = "HTTP Polling"  # Default mode
```

#### Current (WebSocket is default):
```python
st.session_state.scan_mode = "WebSocket"  # DEFAULT: WebSocket for real-time streaming
```

#### Radio Button Order Changed:

**Before:**
```python
scan_mode = st.sidebar.radio(
    "Select Mode:",
    ["HTTP Polling (60s)", "WebSocket Streaming (<1s)"],
    help="HTTP: Scans every 60 seconds | WebSocket: Real-time tick updates"
)
```

**After:**
```python
scan_mode = st.sidebar.radio(
    "Select Mode:",
    ["WebSocket Streaming (<1s)", "HTTP Polling (60s)"],  # WebSocket first!
    help="WebSocket: Real-time tick updates (RECOMMENDED) | HTTP: Scans every 60 seconds (fallback)"
)
```

---

## HTTP Polling Code Still Present (For Fallback)

### Where HTTP Polling Code Lives:

#### 1. **scanner_dashboard.py** (Lines ~100-120)
```python
# Auto-scan toggle (for HTTP mode only)
st.sidebar.markdown("---")
if st.session_state.scan_mode == "HTTP":
    auto_scan = st.sidebar.checkbox("Enable Auto-Scan (every 60s)")
else:
    auto_scan = False
    st.sidebar.info("🔴 LIVE - WebSocket streaming active")
```

**Status:** ✅ Still functional but only activated when user manually switches to HTTP mode

#### 2. **scanner_dashboard.py** (Lines ~180-200)
```python
if st.session_state.scan_mode == "HTTP":
    stats = st.session_state.scanner.get_statistics()
    st.sidebar.metric("Symbols", stats['symbols_count'])
    st.sidebar.metric("Total Scans", stats['symbols_scanned'])
    st.sidebar.metric("Signals Generated", stats['signals_generated'])
```

**Status:** ✅ Conditional display - only shows when HTTP mode is active

#### 3. **scanner_dashboard.py** (Lines ~400-430)
```python
# Auto-refresh if HTTP auto-scan is enabled
elif auto_scan:
    # Check if enough time has passed since last scan
    should_scan = False
    
    if st.session_state.last_scan_time is None:
        should_scan = True
    else:
        time_since_scan = (datetime.now() - st.session_state.last_scan_time).total_seconds()
        should_scan = time_since_scan >= 60  # 60 seconds interval
    
    if should_scan:
        # Automatically trigger scan
        with st.spinner("Auto-scanning all NIFTY 50 stocks..."):
            signals = st.session_state.scanner.scan_all_symbols()
            # ... rest of HTTP polling logic
```

**Status:** ✅ Runs only when user manually enables HTTP mode

#### 4. **src/scanner/multi_symbol_scanner.py**
This file implements the HTTP polling logic:
```python
class MultiSymbolScanner:
    def scan_all_symbols(self):
        """Scan all symbols using HTTP data fetcher"""
        # ... HTTP polling implementation
```

**Status:** ✅ Still fully functional, used as fallback

#### 5. **src/data/data_fetcher.py**
HTTP-based data fetching:
```python
class DataFetcher:
    def get_historical_data(self, symbol, interval='5min', days=5):
        """Fetch historical data via HTTP API"""
        # ... HTTP API calls with rate limiting
```

**Status:** ✅ Still functional, used when HTTP mode is selected

---

## How to Switch Between Modes

### In Scanner Dashboard:

**WebSocket Mode (Default):**
- Automatically starts when you open the dashboard
- Shows "🔴 LIVE - WebSocket streaming active" in sidebar
- Real-time updates every ~1 second

**Switch to HTTP Mode:**
1. Go to sidebar
2. Under "⚡ Scan Mode" section
3. Select "HTTP Polling (60s)"
4. Enable "Auto-Scan (every 60s)" checkbox
5. HTTP polling will start

**Switch Back to WebSocket:**
1. Select "WebSocket Streaming (<1s)"
2. WebSocket will reconnect automatically
3. HTTP polling stops

---

## Code Flow Comparison

### WebSocket Flow (Default):
```
1. scanner_dashboard.py starts
2. Default mode = "WebSocket"
3. Check if WebSocket stream exists
4. If not, initialize WebSocket connection:
   - Load instrument_tokens.json
   - Create RealtimeDataStream
   - Subscribe to all symbols
   - Start streaming
5. Real-time updates every ~1s
```

### HTTP Polling Flow (Fallback):
```
1. User manually switches to HTTP mode
2. WebSocket stops (if running)
3. User enables "Auto-Scan"
4. Every 60 seconds:
   - Call MultiSymbolScanner.scan_all_symbols()
   - Fetch data for each symbol via HTTP
   - Rate limiting applied (3 req/s)
   - Generate signals
   - Update display
```

---

## Performance Comparison

| Feature | WebSocket (Default) | HTTP Polling (Fallback) |
|---------|---------------------|-------------------------|
| **Latency** | < 1 second | 60 seconds |
| **API Calls** | Initial + streaming | 3 calls/second |
| **Rate Limits** | No issue | Can hit limits |
| **Real-time** | Yes | No |
| **Bandwidth** | Low (after connect) | Higher |
| **Best For** | Live trading | Testing/debugging |
| **Reliability** | High | Medium |

---

## When HTTP Mode Might Be Useful

### Debugging Scenarios:
- Testing strategy logic without real-time data
- Analyzing historical behavior
- Reducing API load during development

### Testing Scenarios:
- Verifying signal generation logic
- Checking scanner statistics
- Testing alert system

### Fallback Scenarios:
- WebSocket connection issues
- API restrictions
- Network instability

---

## Migration Notes

### What Changed in Code:

1. **Default Mode**: HTTP → WebSocket
2. **UI Order**: HTTP first → WebSocket first
3. **Help Text**: Added "RECOMMENDED" to WebSocket
4. **Conditional Logic**: WebSocket now primary branch

### What Stayed the Same:

1. ✅ HTTP polling code fully functional
2. ✅ MultiSymbolScanner unchanged
3. ✅ DataFetcher unchanged
4. ✅ Rate limiting still works
5. ✅ All HTTP features available

### Breaking Changes:

**NONE!** All existing functionality is preserved. Users can still:
- Switch to HTTP mode manually
- Use HTTP polling for testing
- Access all HTTP features
- Run auto-scan with HTTP

---

## Reverting to HTTP Default (If Needed)

If you ever need to make HTTP the default again:

### scanner_dashboard.py:

```python
# Change line ~63:
st.session_state.scan_mode = "HTTP"  # Change back to HTTP

# Change line ~126-127:
scan_mode = st.sidebar.radio(
    "Select Mode:",
    ["HTTP Polling (60s)", "WebSocket Streaming (<1s)"],  # HTTP first
    help="HTTP: Scans every 60 seconds | WebSocket: Real-time tick updates"
)

# Change line ~134-135:
if scan_mode == "HTTP Polling (60s)":
    st.session_state.scan_mode = "HTTP"
else:
    st.session_state.scan_mode = "WebSocket"
    # Stop WebSocket if running...
```

Then commit and push:
```bash
git add scanner_dashboard.py
git commit -m "Revert to HTTP polling as default"
git push
```

---

## Summary

✅ **WebSocket is now default** - Real-time streaming for live trading  
✅ **HTTP still available** - Fallback mode for testing/debugging  
✅ **No code deleted** - All HTTP functionality preserved  
✅ **Easy to switch** - One click in UI to change modes  
✅ **Fully backward compatible** - No breaking changes

**Recommendation:** Keep WebSocket as default for best performance in live trading scenarios. Use HTTP only when necessary for debugging or when WebSocket is unavailable.

---

*HTTP polling code is NOT deleted - it's just deprioritized in favor of superior WebSocket streaming.*
