# Installation Guide - Alternative Methods

If the automatic setup fails due to network issues, follow these manual steps:

## Method 1: Install Core Dependencies First

Install packages one by one to avoid timeouts:

```powershell
# Core packages
pip install pandas numpy

# Data fetching
pip install yfinance

# Configuration
pip install python-dotenv pyyaml

# Technical analysis
pip install pandas-ta

# Visualization
pip install matplotlib plotly streamlit

# Utilities
pip install requests pytz schedule

# Testing
pip install pytest pytest-cov
```

## Method 2: Install Without Version Pinning

```powershell
pip install pandas numpy yfinance python-dotenv pyyaml pandas-ta matplotlib plotly streamlit requests pytz schedule pytest pytest-cov
```

## Method 3: Increase Timeout

```powershell
pip install -r requirements.txt --timeout 100 --retries 5
```

## Method 4: Use a Mirror (if in certain regions)

```powershell
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## Verify Installation

After installing, verify everything works:

```powershell
python test_functionality.py
```

## Known Issues

### TA-Lib Installation
The `ta-lib` package may fail on Windows. It's optional - the bot uses `pandas-ta` as the main library.

If you need TA-Lib:
1. Download the wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
2. Install: `pip install TA_Lib‑0.4.XX‑cpXX‑cpXX‑win_amd64.whl`

Or simply remove it from requirements.txt - the bot will work fine without it.

## Minimum Required Packages

The bot can run with just these core packages:

```powershell
pip install pandas numpy yfinance pyyaml python-dotenv streamlit plotly
```

All other packages add nice-to-have features but aren't strictly necessary.

## Next Steps

Once dependencies are installed:

1. **Run test**: `python test_functionality.py`
2. **Start bot**: `python main.py`
3. **Start dashboard**: `streamlit run dashboard/app.py`

## Troubleshooting

**ImportError: No module named 'X'**
- Install the specific package: `pip install X`

**Network timeout**
- Try Method 3 with increased timeout
- Or install packages individually (Method 1)

**DLL load failed (Windows)**
- Install Visual C++ Redistributable
- Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
