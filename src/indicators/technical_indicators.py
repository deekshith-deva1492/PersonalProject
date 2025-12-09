"""
Technical Indicators
Calculate various technical indicators for trading analysis
"""

import pandas as pd
import numpy as np
from typing import Tuple

from src.utils.logger import get_logger
from src.utils.config import config

logger = get_logger('technical_indicators', config.get('logging'))


class TechnicalIndicators:
    """Calculate technical indicators"""
    
    def __init__(self):
        """Initialize technical indicators calculator"""
        self.strategy_config = config.get_strategy_config()
        self.indicator_config = self.strategy_config.get('indicators', {})
    
    def calculate_rsi(
        self,
        df: pd.DataFrame,
        period: int = None,
        column: str = 'close'
    ) -> pd.DataFrame:
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            df: Input DataFrame
            period: RSI period (default from config)
            column: Column to calculate RSI on
            
        Returns:
            DataFrame with RSI column
        """
        if period is None:
            period = self.indicator_config.get('rsi_period', 14)
        
        df = df.copy()
        
        # Calculate price changes
        delta = df[column].diff()
        
        # Separate gains and losses
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # Calculate RS and RSI
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        logger.debug(f"Calculated RSI with period {period}")
        return df
    
    def calculate_macd(
        self,
        df: pd.DataFrame,
        fast: int = None,
        slow: int = None,
        signal: int = None,
        column: str = 'close'
    ) -> pd.DataFrame:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            df: Input DataFrame
            fast: Fast EMA period (default from config)
            slow: Slow EMA period (default from config)
            signal: Signal line period (default from config)
            column: Column to calculate MACD on
            
        Returns:
            DataFrame with MACD columns
        """
        if fast is None:
            fast = self.indicator_config.get('macd_fast', 12)
        if slow is None:
            slow = self.indicator_config.get('macd_slow', 26)
        if signal is None:
            signal = self.indicator_config.get('macd_signal', 9)
        
        df = df.copy()
        
        # Calculate EMAs
        ema_fast = df[column].ewm(span=fast, adjust=False).mean()
        ema_slow = df[column].ewm(span=slow, adjust=False).mean()
        
        # Calculate MACD line
        df['macd'] = ema_fast - ema_slow
        
        # Calculate signal line
        df['macd_signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
        
        # Calculate histogram
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        logger.debug(f"Calculated MACD ({fast}/{slow}/{signal})")
        return df
    
    def calculate_moving_averages(
        self,
        df: pd.DataFrame,
        short: int = None,
        long: int = None,
        column: str = 'close'
    ) -> pd.DataFrame:
        """
        Calculate moving averages
        
        Args:
            df: Input DataFrame
            short: Short MA period (default from config)
            long: Long MA period (default from config)
            column: Column to calculate MA on
            
        Returns:
            DataFrame with MA columns
        """
        if short is None:
            short = self.indicator_config.get('ma_short', 20)
        if long is None:
            long = self.indicator_config.get('ma_long', 50)
        
        df = df.copy()
        
        # Simple Moving Averages
        df[f'sma_{short}'] = df[column].rolling(window=short).mean()
        df[f'sma_{long}'] = df[column].rolling(window=long).mean()
        
        # Exponential Moving Averages
        df[f'ema_{short}'] = df[column].ewm(span=short, adjust=False).mean()
        df[f'ema_{long}'] = df[column].ewm(span=long, adjust=False).mean()
        
        logger.debug(f"Calculated moving averages ({short}/{long})")
        return df
    
    def calculate_bollinger_bands(
        self,
        df: pd.DataFrame,
        period: int = None,
        std_dev: float = None,
        column: str = 'close'
    ) -> pd.DataFrame:
        """
        Calculate Bollinger Bands
        
        Args:
            df: Input DataFrame
            period: Period for moving average (default from config)
            std_dev: Number of standard deviations (default from config)
            column: Column to calculate bands on
            
        Returns:
            DataFrame with Bollinger Band columns
        """
        if period is None:
            period = self.indicator_config.get('bb_period', 20)
        if std_dev is None:
            std_dev = self.indicator_config.get('bb_std', 2)
        
        df = df.copy()
        
        # Calculate middle band (SMA)
        df['bb_middle'] = df[column].rolling(window=period).mean()
        
        # Calculate standard deviation
        rolling_std = df[column].rolling(window=period).std()
        
        # Calculate upper and lower bands
        df['bb_upper'] = df['bb_middle'] + (rolling_std * std_dev)
        df['bb_lower'] = df['bb_middle'] - (rolling_std * std_dev)
        
        # Calculate bandwidth
        df['bb_bandwidth'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        
        logger.debug(f"Calculated Bollinger Bands (period={period}, std={std_dev})")
        return df
    
    def calculate_atr(
        self,
        df: pd.DataFrame,
        period: int = 14
    ) -> pd.DataFrame:
        """
        Calculate Average True Range (ATR)
        
        Args:
            df: Input DataFrame with high, low, close
            period: ATR period
            
        Returns:
            DataFrame with ATR column
        """
        df = df.copy()
        
        # True Range
        df['tr1'] = df['high'] - df['low']
        df['tr2'] = abs(df['high'] - df['close'].shift())
        df['tr3'] = abs(df['low'] - df['close'].shift())
        
        df['true_range'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
        
        # ATR
        df['atr'] = df['true_range'].rolling(window=period).mean()
        
        # Clean up temporary columns
        df.drop(['tr1', 'tr2', 'tr3', 'true_range'], axis=1, inplace=True)
        
        logger.debug(f"Calculated ATR with period {period}")
        return df
    
    def calculate_vwap(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Volume Weighted Average Price (VWAP)
        
        Args:
            df: Input DataFrame with high, low, close, volume
            
        Returns:
            DataFrame with VWAP column
        """
        df = df.copy()
        
        # Typical price
        df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
        
        # VWAP calculation
        df['vwap'] = (df['typical_price'] * df['volume']).cumsum() / df['volume'].cumsum()
        
        df.drop('typical_price', axis=1, inplace=True)
        
        logger.debug("Calculated VWAP")
        return df
    
    def calculate_volume_sma(self, df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """
        Calculate average volume over a period
        
        Args:
            df: Input DataFrame with volume
            period: Period for average (default 20)
            
        Returns:
            DataFrame with volume_avg column
        """
        df = df.copy()
        df['volume_avg'] = df['volume'].rolling(window=period).mean()
        logger.debug(f"Calculated {period}-period average volume")
        return df
    
    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all technical indicators at once
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with all indicators
        """
        logger.info("Calculating all technical indicators")
        
        df = self.calculate_rsi(df)
        df = self.calculate_macd(df)
        df = self.calculate_moving_averages(df)
        df = self.calculate_bollinger_bands(df)
        df = self.calculate_atr(df)
        df = self.calculate_vwap(df)
        df = self.calculate_volume_sma(df, period=20)  # Add 20-period average volume
        
        logger.info("All indicators calculated successfully")
        return df
