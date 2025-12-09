"""
Data Processor
Cleans and preprocesses market data
"""

import pandas as pd
import numpy as np
from typing import Optional

from src.utils.logger import get_logger
from src.utils.config import config

logger = get_logger('data_processor', config.get('logging'))


class DataProcessor:
    """Process and clean market data"""
    
    def __init__(self):
        """Initialize data processor"""
        logger.info("Initialized DataProcessor")
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean data by handling missing values and outliers
        
        Args:
            df: Input DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        if df.empty:
            return df
        
        df = df.copy()
        
        # Remove duplicates
        df.drop_duplicates(inplace=True)
        
        # Handle missing values
        df.fillna(method='ffill', inplace=True)
        df.fillna(method='bfill', inplace=True)
        
        # Remove rows with any remaining NaN values
        df.dropna(inplace=True)
        
        logger.info(f"Cleaned data: {len(df)} rows remaining")
        return df
    
    def add_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add return columns to DataFrame
        
        Args:
            df: Input DataFrame with 'close' column
            
        Returns:
            DataFrame with returns columns
        """
        if df.empty or 'close' not in df.columns:
            return df
        
        df = df.copy()
        
        # Simple returns
        df['returns'] = df['close'].pct_change()
        
        # Log returns
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        
        return df
    
    def add_volume_profile(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add volume analysis columns
        
        Args:
            df: Input DataFrame with 'volume' column
            
        Returns:
            DataFrame with volume profile columns
        """
        if df.empty or 'volume' not in df.columns:
            return df
        
        df = df.copy()
        
        # Volume moving average
        df['volume_ma_20'] = df['volume'].rolling(window=20).mean()
        
        # Relative volume
        df['relative_volume'] = df['volume'] / df['volume_ma_20']
        
        # Volume trend
        df['volume_trend'] = df['volume'].rolling(window=5).mean() / df['volume'].rolling(window=20).mean()
        
        return df
    
    def add_price_levels(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add support and resistance levels
        
        Args:
            df: Input DataFrame with OHLC columns
            
        Returns:
            DataFrame with support/resistance levels
        """
        if df.empty:
            return df
        
        df = df.copy()
        
        # Daily high/low
        df['daily_high'] = df['high'].rolling(window=20).max()
        df['daily_low'] = df['low'].rolling(window=20).min()
        
        # Pivot points (standard)
        df['pivot'] = (df['high'] + df['low'] + df['close']) / 3
        
        return df
    
    def filter_by_time(
        self,
        df: pd.DataFrame,
        start_time: str = "09:30",
        end_time: str = "16:00"
    ) -> pd.DataFrame:
        """
        Filter data by time of day
        
        Args:
            df: Input DataFrame with datetime index or column
            start_time: Start time (HH:MM format)
            end_time: End time (HH:MM format)
            
        Returns:
            Filtered DataFrame
        """
        if df.empty:
            return df
        
        df = df.copy()
        
        # Ensure we have a datetime column
        if 'datetime' not in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df.index):
                df['datetime'] = df.index
            else:
                return df
        
        # Convert to datetime if needed
        df['datetime'] = pd.to_datetime(df['datetime'])
        
        # Extract time
        df['time'] = df['datetime'].dt.time
        
        # Filter by time range
        start = pd.to_datetime(start_time, format='%H:%M').time()
        end = pd.to_datetime(end_time, format='%H:%M').time()
        
        df = df[(df['time'] >= start) & (df['time'] <= end)]
        df.drop('time', axis=1, inplace=True)
        
        logger.info(f"Filtered data by time: {len(df)} rows remaining")
        return df
    
    def resample_data(
        self,
        df: pd.DataFrame,
        timeframe: str = '15min'
    ) -> pd.DataFrame:
        """
        Resample data to different timeframe
        
        Args:
            df: Input DataFrame with datetime index or column
            timeframe: Target timeframe (e.g., '15min', '1h')
            
        Returns:
            Resampled DataFrame
        """
        if df.empty:
            return df
        
        df = df.copy()
        
        # Set datetime as index
        if 'datetime' in df.columns:
            df.set_index('datetime', inplace=True)
        
        # Resample OHLCV data
        resampled = pd.DataFrame()
        resampled['open'] = df['open'].resample(timeframe).first()
        resampled['high'] = df['high'].resample(timeframe).max()
        resampled['low'] = df['low'].resample(timeframe).min()
        resampled['close'] = df['close'].resample(timeframe).last()
        resampled['volume'] = df['volume'].resample(timeframe).sum()
        
        resampled.reset_index(inplace=True)
        
        logger.info(f"Resampled data to {timeframe}: {len(resampled)} rows")
        return resampled
