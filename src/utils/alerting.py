"""
Alert System for Trading Bot
Provides multiple alert mechanisms: desktop notifications, sound, email, Telegram
"""

import logging
from typing import List, Optional
from datetime import datetime
import os

# Desktop notifications
try:
    from plyer import notification
    DESKTOP_ALERTS_AVAILABLE = True
except ImportError:
    DESKTOP_ALERTS_AVAILABLE = False
    
# Sound alerts
try:
    import winsound  # Windows only
    SOUND_ALERTS_AVAILABLE = True
except ImportError:
    SOUND_ALERTS_AVAILABLE = False

# Email alerts
try:
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    EMAIL_ALERTS_AVAILABLE = True
except ImportError:
    EMAIL_ALERTS_AVAILABLE = False

# Telegram alerts
try:
    import requests
    TELEGRAM_ALERTS_AVAILABLE = True
except ImportError:
    TELEGRAM_ALERTS_AVAILABLE = False

logger = logging.getLogger(__name__)


class AlertManager:
    """Manages all alert mechanisms for trading signals"""
    
    def __init__(self, config: Optional[dict] = None):
        """
        Initialize alert manager
        
        Args:
            config: Alert configuration dictionary
        """
        self.config = config or {}
        
        # Alert preferences
        self.desktop_enabled = self.config.get('desktop_alerts', True)
        self.sound_enabled = self.config.get('sound_alerts', True)
        self.email_enabled = self.config.get('email_alerts', False)
        self.telegram_enabled = self.config.get('telegram_alerts', False)
        
        # Email configuration
        self.email_from = os.getenv('ALERT_EMAIL_FROM')
        self.email_to = os.getenv('ALERT_EMAIL_TO')
        self.email_password = os.getenv('ALERT_EMAIL_PASSWORD')
        self.smtp_server = os.getenv('ALERT_SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('ALERT_SMTP_PORT', '587'))
        
        # Telegram configuration
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        # Check capabilities
        self._check_capabilities()
        
    def _check_capabilities(self):
        """Check which alert mechanisms are available"""
        if self.desktop_enabled and not DESKTOP_ALERTS_AVAILABLE:
            logger.warning("Desktop alerts enabled but 'plyer' not installed. Run: pip install plyer")
            self.desktop_enabled = False
            
        if self.sound_enabled and not SOUND_ALERTS_AVAILABLE:
            logger.warning("Sound alerts not available (Windows only)")
            self.sound_enabled = False
            
        if self.email_enabled and not EMAIL_ALERTS_AVAILABLE:
            logger.warning("Email alerts enabled but 'smtplib' not available")
            self.email_enabled = False
        elif self.email_enabled and not all([self.email_from, self.email_to, self.email_password]):
            logger.warning("Email alerts enabled but credentials not configured in .env")
            self.email_enabled = False
            
        if self.telegram_enabled and not TELEGRAM_ALERTS_AVAILABLE:
            logger.warning("Telegram alerts enabled but 'requests' not installed")
            self.telegram_enabled = False
        elif self.telegram_enabled and not all([self.telegram_bot_token, self.telegram_chat_id]):
            logger.warning("Telegram alerts enabled but credentials not configured in .env")
            self.telegram_enabled = False
    
    def send_signal_alert(self, signal):
        """
        Send alerts for a new trading signal
        
        Args:
            signal: Signal object with trading information
        """
        title = f"🔔 {signal.signal_type.value} SIGNAL: {signal.symbol}"
        message = self._format_signal_message(signal)
        
        # Send all enabled alerts
        if self.desktop_enabled:
            self._send_desktop_alert(title, message)
            
        if self.sound_enabled:
            self._play_alert_sound(signal.signal_type.value)
            
        if self.email_enabled:
            self._send_email_alert(title, message, signal)
            
        if self.telegram_enabled:
            self._send_telegram_alert(title, message)
    
    def send_multiple_signals_alert(self, signals: List):
        """
        Send alerts for multiple signals found in a scan
        
        Args:
            signals: List of Signal objects
        """
        if not signals:
            return
            
        buy_signals = [s for s in signals if s.signal_type.value == 'BUY']
        sell_signals = [s for s in signals if s.signal_type.value == 'SELL']
        
        title = f"🔍 {len(signals)} Signal(s) Found!"
        message = f"BUY: {len(buy_signals)} | SELL: {len(sell_signals)}\n\n"
        
        for sig in signals[:5]:  # Show first 5
            message += f"• {sig.signal_type.value} {sig.symbol} @ ₹{sig.price:.2f}\n"
        
        if len(signals) > 5:
            message += f"\n... and {len(signals) - 5} more signals"
        
        # Send alerts
        if self.desktop_enabled:
            self._send_desktop_alert(title, message)
            
        if self.sound_enabled:
            self._play_alert_sound('MULTIPLE')
            
        if self.email_enabled:
            detailed_message = "\n\n".join([self._format_signal_message(s) for s in signals])
            self._send_email_alert(title, detailed_message, signals[0])
            
        if self.telegram_enabled:
            self._send_telegram_alert(title, message)
    
    def _format_signal_message(self, signal) -> str:
        """Format signal information for alert"""
        msg = f"{signal.symbol}\n"
        msg += f"Price: ₹{signal.price:.2f}\n"
        msg += f"Strength: {signal.strength:.1%}\n"
        
        if hasattr(signal, 'stop_loss') and signal.stop_loss:
            msg += f"Stop Loss: ₹{signal.stop_loss:.2f}\n"
        if hasattr(signal, 'take_profit') and signal.take_profit:
            msg += f"Take Profit: ₹{signal.take_profit:.2f}\n"
            
        return msg
    
    def _send_desktop_alert(self, title: str, message: str):
        """Send desktop notification"""
        try:
            notification.notify(
                title=title,
                message=message,
                app_name='Trading Bot',
                timeout=10  # Show for 10 seconds
            )
            logger.info(f"Desktop notification sent: {title}")
        except Exception as e:
            logger.error(f"Failed to send desktop notification: {e}")
    
    def _play_alert_sound(self, signal_type: str):
        """Play sound alert"""
        try:
            if signal_type == 'BUY':
                # Higher pitch for BUY
                winsound.Beep(1000, 300)  # 1000 Hz for 300ms
                winsound.Beep(1200, 300)
            elif signal_type == 'SELL':
                # Lower pitch for SELL
                winsound.Beep(800, 300)   # 800 Hz for 300ms
                winsound.Beep(600, 300)
            else:  # MULTIPLE
                # Triple beep
                for _ in range(3):
                    winsound.Beep(1000, 200)
            
            logger.info(f"Alert sound played: {signal_type}")
        except Exception as e:
            logger.error(f"Failed to play alert sound: {e}")
    
    def _send_email_alert(self, subject: str, body: str, signal):
        """Send email alert"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = self.email_to
            msg['Subject'] = subject
            
            # Add timestamp
            body = f"Alert Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}\n\n{body}"
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_from, self.email_password)
                server.send_message(msg)
            
            logger.info(f"Email alert sent to {self.email_to}")
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    def _send_telegram_alert(self, title: str, message: str):
        """Send Telegram alert"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            
            text = f"<b>{title}</b>\n\n{message}"
            
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Telegram alert sent to chat {self.telegram_chat_id}")
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
    
    def test_alerts(self):
        """Test all enabled alert mechanisms"""
        logger.info("Testing alert mechanisms...")
        
        test_title = "🧪 Test Alert"
        test_message = "This is a test alert from your Trading Bot!"
        
        if self.desktop_enabled:
            self._send_desktop_alert(test_title, test_message)
            
        if self.sound_enabled:
            self._play_alert_sound('BUY')
            
        if self.email_enabled:
            self._send_email_alert(test_title, test_message, None)
            
        if self.telegram_enabled:
            self._send_telegram_alert(test_title, test_message)
        
        logger.info("Alert test complete!")
