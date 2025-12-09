"""
Intraday Trading Strategy - Ultra Simple Trend Following
Trade only with the trend using 15m EMA, buy dips/sell spikes on 5m timeframe
"""

import pandas as pd
from typing import List, Tuple

from src.strategies.base_strategy import BaseStrategy, Signal, SignalType
from src.indicators.technical_indicators import TechnicalIndicators
from src.utils.logger import get_logger
from src.utils.config import config

logger = get_logger('intraday_strategy', config.get('logging'))


class IntradayStrategy(BaseStrategy):
    """Ultra-simple intraday strategy: Trade with trend, buy dips, sell spikes"""
    
    def __init__(self):
        """Initialize intraday strategy"""
        super().__init__("TrendFollowingDipSpike")
        
        self.indicators = TechnicalIndicators()
        self.indicator_config = self.strategy_config.get('indicators', {})
        self.entry_config = self.strategy_config.get('entry', {})
        
        # MUST-HAVE FILTERS (3 mandatory - all must pass)
        self.ema_period = 50  # Trend bias
        self.min_volume_multiplier = 1.2  # Volume >= 1.2x
        self.min_candle_range = 0.0015  # Significant candle (0.15%+)
        
        # OPTIONAL CONFIDENCE BOOSTERS (5 available - each adds +1)
        self.rsi_oversold = 30  # RSI extreme
        self.rsi_overbought = 70
        self.vwap_band_threshold = 0.002  # VWAP confluence (within 0.2%)
        self.trend_strength_threshold = 0.005  # EMA separation (0.5%+)
        
        # Signal strength
        # 3 = valid (all 3 mandatory passed)
        # 4 = strong (3 mandatory + 1 booster)
        # 5+ = high probability (3 mandatory + 2+ boosters)
    
    def generate_signals(self, df: pd.DataFrame, symbol: str) -> List[Signal]:
        """
        Generate trading signals
        
        Args:
            df: DataFrame with price data
            symbol: Stock symbol
            
        Returns:
            List of trading signals
        """
        if not self.validate_data(df):
            logger.error(f"Invalid data for {symbol}")
            return []
        
        # Calculate all indicators
        df = self.indicators.calculate_all_indicators(df)
        
        signals = []
        
        # Iterate through recent data to find signals
        for i in range(len(df) - 1, max(len(df) - 10, 0), -1):
            row = df.iloc[i]
            
            # Check if we have valid indicator values
            if pd.isna(row.get('rsi')) or pd.isna(row.get('macd')):
                continue
            
            # Check entry conditions
            should_buy, buy_reason = self.get_entry_conditions(row)
            
            if should_buy:
                # Calculate signal strength
                conditions = self._get_buy_conditions(row)
                strength = self.calculate_signal_strength(conditions)
                
                # Calculate stop loss and take profit
                entry_price = row['close']
                stop_loss = entry_price * (1 - 0.003)  # 0.3% stop loss
                take_profit = entry_price * (1 + 0.007)  # 0.7% take profit
                
                # Build detailed conditions list
                conditions_met = []
                if conditions.get('in_uptrend'):
                    conditions_met.append(f"✅ In UPTREND: Price ₹{entry_price:.2f} > EMA50 ₹{row.get('ema_50', 0):.2f}")
                if conditions.get('rsi_oversold'):
                    conditions_met.append(f"✅ RSI OVERSOLD: {row['rsi']:.1f} < {self.rsi_oversold} (dip detected)")
                if conditions.get('at_vwap_lower'):
                    vwap = row.get('vwap', entry_price)
                    conditions_met.append(f"✅ At VWAP LOWER: ₹{entry_price:.2f} <= ₹{vwap * 0.998:.2f} (mean reversion opportunity)")
                if conditions.get('bullish_candle'):
                    conditions_met.append(f"✅ BULLISH REVERSAL: Close ₹{row['close']:.2f} > Open ₹{row['open']:.2f}")
                if conditions.get('volume_confirmation'):
                    vol = row.get('volume', 0)
                    vol_avg = row.get('volume_avg', 0)
                    vol_ratio = vol / vol_avg if vol_avg > 0 else 0
                    conditions_met.append(f"✅ VOLUME CONFIRMATION: {vol:,.0f} >= {vol_avg * 1.2:,.0f} ({vol_ratio:.1f}x avg)")
                if conditions.get('macd_bullish'):
                    macd = row.get('macd', 0)
                    macd_signal = row.get('macd_signal', 0)
                    conditions_met.append(f"✅ MACD BULLISH: {macd:.2f} > Signal {macd_signal:.2f} (upward momentum)")
                if conditions.get('trend_strength'):
                    ema_20 = row.get('ema_20', 0)
                    ema_50 = row.get('ema_50', 0)
                    ema_separation = abs(ema_20 - ema_50) / ema_50 * 100 if ema_50 > 0 else 0
                    conditions_met.append(f"✅ TREND STRENGTH: EMA separation {ema_separation:.2f}% >= {self.trend_strength_threshold*100:.1f}% (avoiding sideways market)")
                if conditions.get('candle_range'):
                    high = row.get('high', 0)
                    low = row.get('low', 0)
                    close = row.get('close', 1)
                    candle_range = (high - low) / close * 100 if close > 0 else 0
                    conditions_met.append(f"✅ CANDLE RANGE: {candle_range:.3f}% >= {self.min_candle_range*100:.2f}% (real movement, not micro-candle)")
                
                # Capture indicator values
                indicators = {
                    'RSI': row.get('rsi', 0),
                    'EMA_20': row.get('ema_20', 0),
                    'EMA_50': row.get('ema_50', 0),
                    'VWAP': row.get('vwap', 0),
                    'MACD': row.get('macd', 0),
                    'MACD_Signal': row.get('macd_signal', 0),
                    'Close': row['close'],
                    'Open': row['open'],
                    'High': row['high'],
                    'Low': row['low'],
                    'Volume': row.get('volume', 0)
                }
                
                signal = Signal(
                    symbol=symbol,
                    signal_type=SignalType.BUY,
                    price=entry_price,
                    strength=strength,
                    reason=buy_reason,
                    timestamp=row.get('datetime', pd.Timestamp.now()),
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    indicators=indicators,
                    conditions_met=conditions_met
                )
                signals.append(signal)
                logger.info(f"Generated BUY signal for {symbol}: {buy_reason}")
            
            # Check for sell signals
            should_sell, sell_reason = self._check_sell_conditions(row)
            
            if should_sell:
                conditions = self._get_sell_conditions(row)
                strength = self.calculate_signal_strength(conditions)
                
                # Calculate stop loss and take profit for short
                entry_price = row['close']
                stop_loss = entry_price * (1 + 0.003)  # 0.3% stop loss (higher for short)
                take_profit = entry_price * (1 - 0.007)  # 0.7% take profit (lower for short)
                
                # Build detailed conditions list
                conditions_met = []
                if conditions.get('in_downtrend'):
                    conditions_met.append(f"✅ In DOWNTREND: Price ₹{entry_price:.2f} < EMA50 ₹{row.get('ema_50', 0):.2f}")
                if conditions.get('rsi_overbought'):
                    conditions_met.append(f"✅ RSI OVERBOUGHT: {row['rsi']:.1f} > {self.rsi_overbought} (spike detected)")
                if conditions.get('at_vwap_upper'):
                    vwap = row.get('vwap', entry_price)
                    conditions_met.append(f"✅ At VWAP UPPER: ₹{entry_price:.2f} >= ₹{vwap * 1.002:.2f} (mean reversion opportunity)")
                if conditions.get('bearish_candle'):
                    conditions_met.append(f"✅ BEARISH REVERSAL: Close ₹{row['close']:.2f} < Open ₹{row['open']:.2f}")
                if conditions.get('volume_confirmation'):
                    vol = row.get('volume', 0)
                    vol_avg = row.get('volume_avg', 0)
                    vol_ratio = vol / vol_avg if vol_avg > 0 else 0
                    conditions_met.append(f"✅ VOLUME CONFIRMATION: {vol:,.0f} >= {vol_avg * 1.2:,.0f} ({vol_ratio:.1f}x avg)")
                if conditions.get('macd_bearish'):
                    macd = row.get('macd', 0)
                    macd_signal = row.get('macd_signal', 0)
                    conditions_met.append(f"✅ MACD BEARISH: {macd:.2f} < Signal {macd_signal:.2f} (downward momentum)")
                if conditions.get('trend_strength'):
                    ema_20 = row.get('ema_20', 0)
                    ema_50 = row.get('ema_50', 0)
                    ema_separation = abs(ema_20 - ema_50) / ema_50 * 100 if ema_50 > 0 else 0
                    conditions_met.append(f"✅ TREND STRENGTH: EMA separation {ema_separation:.2f}% >= {self.trend_strength_threshold*100:.1f}% (avoiding sideways market)")
                if conditions.get('candle_range'):
                    high = row.get('high', 0)
                    low = row.get('low', 0)
                    close = row.get('close', 1)
                    candle_range = (high - low) / close * 100 if close > 0 else 0
                    conditions_met.append(f"✅ CANDLE RANGE: {candle_range:.3f}% >= {self.min_candle_range*100:.2f}% (real movement, not micro-candle)")
                
                # Capture indicator values
                indicators = {
                    'RSI': row.get('rsi', 0),
                    'EMA_20': row.get('ema_20', 0),
                    'EMA_50': row.get('ema_50', 0),
                    'VWAP': row.get('vwap', 0),
                    'MACD': row.get('macd', 0),
                    'MACD_Signal': row.get('macd_signal', 0),
                    'Close': row['close'],
                    'Open': row['open'],
                    'High': row['high'],
                    'Low': row['low'],
                    'Volume': row.get('volume', 0)
                }
                
                signal = Signal(
                    symbol=symbol,
                    signal_type=SignalType.SELL,
                    price=entry_price,
                    strength=strength,
                    reason=sell_reason,
                    timestamp=row.get('datetime', pd.Timestamp.now()),
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    indicators=indicators,
                    conditions_met=conditions_met
                )
                signals.append(signal)
                logger.info(f"Generated SELL signal for {symbol}: {sell_reason}")
        
        return signals
    
    def get_entry_conditions(self, row: pd.Series) -> Tuple[bool, str]:
        """
        Simple 3+5 Scoring System
        
        MUST-HAVE (all 3 required):
        1. Trend bias (price vs EMA50)
        2. Volume >= 1.2x average
        3. Candle range >= 0.15%
        
        OPTIONAL CONFIDENCE BOOSTERS (max +5):
        +1 RSI extreme (oversold/overbought)
        +1 MACD improving (aligns with trend)
        +1 VWAP confluence (near band)
        +1 EMA separation (strong trend)
        +1 Candle pattern (bullish/bearish reversal)
        
        Score:
        3 = valid signal
        4 = strong signal
        5+ = high probability signal
        
        Args:
            row: Data row with indicators
            
        Returns:
            Tuple of (should_enter, reason)
        """
        # Check we have required data
        if 'ema_50' not in row or pd.isna(row['ema_50']):
            return False, "No EMA data yet"
        
        # Extract values
        price = row['close']
        open_price = row['open']
        high = row.get('high', price)
        low = row.get('low', price)
        ema_50 = row['ema_50']
        ema_20 = row.get('ema_20', ema_50)
        rsi = row['rsi']
        vwap = row.get('vwap', price)
        macd = row.get('macd', 0)
        macd_signal = row.get('macd_signal', 0)
        volume = row.get('volume', 0)
        volume_avg = row.get('volume_avg', 1)
        
        # ============================================================
        # MUST-HAVE #1: Trend Bias
        # ============================================================
        is_uptrend = price > ema_50
        is_downtrend = price < ema_50
        
        if not (is_uptrend or is_downtrend):
            return False, "No clear trend bias"
        
        # ============================================================
        # MUST-HAVE #2: Volume
        # ============================================================
        volume_ratio = volume / volume_avg if volume_avg > 0 else 0
        if volume_ratio < self.min_volume_multiplier:
            return False, f"Volume too low ({volume_ratio:.1f}x < {self.min_volume_multiplier}x)"
        
        # ============================================================
        # MUST-HAVE #3: Candle Range
        # ============================================================
        candle_range = (high - low) / price if price > 0 else 0
        if candle_range < self.min_candle_range:
            return False, f"Candle too small ({candle_range*100:.2f}% < {self.min_candle_range*100:.2f}%)"
        
        # ============================================================
        # ALL 3 MUST-HAVES PASSED! Score starts at 3
        # ============================================================
        score = 3
        boosters = []
        
        # BOOSTER #1: RSI Extreme (+1)
        if is_uptrend and rsi < self.rsi_oversold:
            score += 1
            boosters.append(f"RSI oversold ({rsi:.1f})")
        elif is_downtrend and rsi > self.rsi_overbought:
            score += 1
            boosters.append(f"RSI overbought ({rsi:.1f})")
        
        # BOOSTER #2: MACD Improving (+1)
        if is_uptrend and macd > macd_signal:
            score += 1
            boosters.append(f"MACD bullish ({macd:.2f}>{macd_signal:.2f})")
        elif is_downtrend and macd < macd_signal:
            score += 1
            boosters.append(f"MACD bearish ({macd:.2f}<{macd_signal:.2f})")
        
        # BOOSTER #3: VWAP Confluence (+1)
        vwap_distance = abs(price - vwap) / vwap if vwap > 0 else 1
        if vwap_distance <= self.vwap_band_threshold:
            score += 1
            boosters.append(f"Near VWAP (±{vwap_distance*100:.2f}%)")
        
        # BOOSTER #4: EMA Separation / Strong Trend (+1)
        ema_separation = abs(ema_20 - ema_50) / ema_50 if ema_50 > 0 else 0
        if ema_separation >= self.trend_strength_threshold:
            score += 1
            boosters.append(f"Strong trend ({ema_separation*100:.2f}%)")
        
        # BOOSTER #5: Candle Pattern (+1)
        is_bullish_candle = price > open_price
        is_bearish_candle = price < open_price
        if is_uptrend and is_bullish_candle:
            score += 1
            boosters.append("Bullish candle")
        elif is_downtrend and is_bearish_candle:
            score += 1
            boosters.append("Bearish candle")
        
        # ============================================================
        # BUILD SIGNAL REASON
        # ============================================================
        signal_type = "BUY" if is_uptrend else "SELL"
        trend_text = "UPTREND" if is_uptrend else "DOWNTREND"
        
        # Must-haves summary
        must_have = f"{trend_text} + Vol {volume_ratio:.1f}x + Candle {candle_range*100:.2f}%"
        
        # Boosters summary
        booster_text = " | ".join(boosters) if boosters else "no boosters"
        
        # Quality level
        if score >= 5:
            quality = "HIGH-PROB"
        elif score >= 4:
            quality = "STRONG"
        else:
            quality = "VALID"
        
        reason = f"{signal_type} [{quality} {score}/8]: {must_have} | {booster_text}"
        
        return True, reason
    
    def _check_sell_conditions(self, row: pd.Series) -> Tuple[bool, str]:
        """
        Check conditions for SELL/SHORT signal
        
        NOTE: Now uses the same tiered scoring system as get_entry_conditions()
        This method just calls get_entry_conditions() for consistency
        """
        return self.get_entry_conditions(row)
    
    def get_exit_conditions(
        self,
        row: pd.Series,
        entry_price: float
    ) -> Tuple[bool, str]:
        """
        STEP 3: Exit Rules (Ultra Simple)
        
        Take Profit: Price returns to VWAP OR 0.4%-0.7% gain
        Stop Loss: Fixed 0.3%
        
        Args:
            row: Current data row
            entry_price: Price at entry
            
        Returns:
            Tuple of (should_exit, reason)
        """
        current_price = row['close']
        pnl_percent = (current_price - entry_price) / entry_price
        
        # STOP LOSS: Fixed 0.3% (small, tight)
        if pnl_percent <= -0.003:  # -0.3%
            return True, f"Stop loss hit: {pnl_percent*100:.2f}%"
        
        # TAKE PROFIT 1: Fixed 0.4% to 0.7% gain
        if pnl_percent >= 0.007:  # 0.7% - take it!
            return True, f"Profit target reached: {pnl_percent*100:.2f}%"
        
        # TAKE PROFIT 2: Price returns to VWAP (mean reversion complete)
        vwap = row.get('vwap', 0)
        if vwap > 0:
            # If we're in profit and price is back near VWAP, exit
            if pnl_percent >= 0.002:  # At least 0.2% in profit
                distance_to_vwap = abs(current_price - vwap) / vwap
                if distance_to_vwap < 0.001:  # Within 0.1% of VWAP
                    return True, f"Price returned to VWAP: {pnl_percent*100:.2f}% profit"
        
        return False, "Hold position"
    
    def _get_buy_conditions(self, row: pd.Series) -> dict:
        """Get all buy conditions for strength calculation"""
        price = row['close']
        ema_50 = row.get('ema_50', price)
        ema_20 = row.get('ema_20', ema_50)
        vwap = row.get('vwap', price)
        
        # Volume confirmation - current volume must be 20% above average
        volume = row.get('volume', 0)
        volume_avg = row.get('volume_avg', 1)  # Default to 1 to avoid division by zero
        has_volume_confirmation = volume >= volume_avg * 1.2
        
        # MACD momentum confirmation - MACD must be above signal line (bullish momentum)
        macd = row.get('macd', 0)
        macd_signal = row.get('macd_signal', 0)
        has_bullish_momentum = macd > macd_signal
        
        # Trend strength confirmation - EMA separation must exceed threshold (avoid sideways)
        ema_separation = abs(ema_20 - ema_50) / ema_50 if ema_50 > 0 else 0
        has_trend_strength = ema_separation >= self.trend_strength_threshold
        
        # Candle range confirmation - candle must have sufficient range (avoid micro-candles)
        high = row.get('high', price)
        low = row.get('low', price)
        candle_range = (high - low) / price if price > 0 else 0
        has_sufficient_range = candle_range >= self.min_candle_range
        
        return {
            'in_uptrend': price > ema_50,
            'rsi_oversold': row['rsi'] < self.rsi_oversold,
            'at_vwap_lower': price <= vwap * 0.998,
            'bullish_candle': row['close'] > row['open'],
            'volume_confirmation': has_volume_confirmation,
            'macd_bullish': has_bullish_momentum,
            'trend_strength': has_trend_strength,
            'candle_range': has_sufficient_range  # NEW: Candle range filter (avoid micro-candles)
        }
    
    def _get_sell_conditions(self, row: pd.Series) -> dict:
        """Get all sell conditions for strength calculation"""
        price = row['close']
        ema_50 = row.get('ema_50', price)
        ema_20 = row.get('ema_20', ema_50)
        vwap = row.get('vwap', price)
        
        # Volume confirmation - current volume must be 20% above average
        volume = row.get('volume', 0)
        volume_avg = row.get('volume_avg', 1)  # Default to 1 to avoid division by zero
        has_volume_confirmation = volume >= volume_avg * 1.2
        
        # MACD momentum confirmation - MACD must be below signal line (bearish momentum)
        macd = row.get('macd', 0)
        macd_signal = row.get('macd_signal', 0)
        has_bearish_momentum = macd < macd_signal
        
        # Trend strength confirmation - EMA separation must exceed threshold (avoid sideways)
        ema_separation = abs(ema_20 - ema_50) / ema_50 if ema_50 > 0 else 0
        has_trend_strength = ema_separation >= self.trend_strength_threshold
        
        # Candle range confirmation - candle must have sufficient range (avoid micro-candles)
        high = row.get('high', price)
        low = row.get('low', price)
        candle_range = (high - low) / price if price > 0 else 0
        has_sufficient_range = candle_range >= self.min_candle_range
        
        return {
            'in_downtrend': price < ema_50,
            'rsi_overbought': row['rsi'] > self.rsi_overbought,
            'at_vwap_upper': price >= vwap * 1.002,
            'bearish_candle': row['close'] < row['open'],
            'volume_confirmation': has_volume_confirmation,
            'macd_bearish': has_bearish_momentum,
            'trend_strength': has_trend_strength,
            'candle_range': has_sufficient_range  # NEW: Candle range filter (avoid micro-candles)
        }
