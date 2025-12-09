"""
Run Dashboard - Helper script to start the trading dashboard
"""
import sys
import os

# Add parent directory to path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now run streamlit
if __name__ == "__main__":
    import streamlit.web.cli as stcli
    import sys
    
    dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard", "app.py")
    sys.argv = ["streamlit", "run", dashboard_path]
    sys.exit(stcli.main())
