"""
Run Scanner Dashboard
Launch the multi-symbol scanner dashboard
"""

import subprocess
import sys

def main():
    """Run the scanner dashboard"""
    print("🔍 Starting NIFTY 50 Scanner Dashboard...")
    print("Dashboard will open in your browser")
    print("Press Ctrl+C to stop\n")
    
    # Run streamlit
    subprocess.run([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "scanner_dashboard.py",
        "--server.port=8505",
        "--server.headless=true"
    ])

if __name__ == '__main__':
    main()
