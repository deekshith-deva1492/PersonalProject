"""
Market Hours Validation Utility
Checks if NSE market is currently open for trading
"""

from datetime import datetime, time
import pytz


def check_market_hours():
    """
    Check if NSE market is currently open for trading
    
    Returns:
        tuple: (is_open: bool, message: str)
        - is_open: True if market is open, False if closed
        - message: Human-readable status message
    """
    # Get current time in IST
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    # Check if it's a weekend
    if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False, f"⚠️ MARKET CLOSED - Weekend (Trading hours: Mon-Fri 9:15 AM - 3:30 PM IST)"
    
    # Define market hours
    market_open_time = time(9, 15)  # 9:15 AM
    market_close_time = time(15, 30)  # 3:30 PM
    
    current_time = now.time()
    
    # Check if current time is before market open
    if current_time < market_open_time:
        return False, f"⚠️ MARKET CLOSED - Market opens at 9:15 AM IST (Current: {now.strftime('%I:%M %p IST')})"
    
    # Check if current time is after market close
    if current_time > market_close_time:
        return False, f"⚠️ MARKET CLOSED - Market closed at 3:30 PM IST (Current: {now.strftime('%I:%M %p IST')})"
    
    # Market is open
    return True, f"✅ MARKET OPEN - Trading active (Current: {now.strftime('%I:%M %p IST')})"


def get_market_status_detailed():
    """
    Get detailed market status information
    
    Returns:
        dict: Detailed market status with timing information
    """
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    is_open, message = check_market_hours()
    
    # Calculate time to next market event
    market_open_time = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close_time = now.replace(hour=15, minute=30, second=0, microsecond=0)
    
    if now.weekday() >= 5:
        # Calculate days until Monday
        days_until_monday = (7 - now.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 1
        next_event = f"Opens Monday at 9:15 AM ({days_until_monday} days)"
    elif now.time() < time(9, 15):
        time_diff = market_open_time - now
        minutes = int(time_diff.total_seconds() / 60)
        next_event = f"Opens in {minutes} minutes"
    elif now.time() > time(15, 30):
        next_event = "Opens tomorrow at 9:15 AM"
    else:
        time_diff = market_close_time - now
        minutes = int(time_diff.total_seconds() / 60)
        next_event = f"Closes in {minutes} minutes"
    
    return {
        'is_open': is_open,
        'message': message,
        'current_time': now.strftime('%I:%M %p IST'),
        'current_day': now.strftime('%A'),
        'next_event': next_event,
        'market_hours': 'Mon-Fri 9:15 AM - 3:30 PM IST'
    }


if __name__ == "__main__":
    # Test the function
    is_open, message = check_market_hours()
    print(message)
    
    print("\nDetailed Status:")
    status = get_market_status_detailed()
    for key, value in status.items():
        print(f"{key}: {value}")
