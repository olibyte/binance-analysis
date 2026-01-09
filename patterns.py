# Import calculation functions
from calculations import (
    calculate_k_envelopes,
    calculate_volume_indicators,
    check_volume_confirmation,
    calculate_rsi,
    detect_rsi_divergence,
    check_rsi_confirmation,
    calculate_macd,
    detect_macd_divergence,
    check_macd_confirmation,
    calculate_adx,
    check_adx_confirmation
)
import pandas as pd
import numpy as np

# Detect Euphoria Pattern
def detect_euphoria_pattern(df):
    """
    Detect Euphoria candlestick pattern.
    
    Bullish Euphoria (bearish signal):
    - Three consecutive red candles (open > close)
    - Close prices decreasing
    - Body sizes (open - close) increasing
    
    Bearish Euphoria (bullish signal):
    - Three consecutive green candles (open < close)
    - Close prices increasing
    - Body sizes (close - open) increasing
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'euphoria_bullish' and 'euphoria_bearish' columns
    """
    df = df.copy()
    df['euphoria_bullish'] = 0  # Bearish signal (red candles)
    df['euphoria_bearish'] = 0  # Bullish signal (green candles)
    
    for i in range(2, len(df)):
        try:
            # Current and previous candles
            curr = df.iloc[i]
            prev1 = df.iloc[i-1]
            prev2 = df.iloc[i-2]
            
            # Bullish Euphoria Pattern (bearish signal - three red candles)
            # All three candles are red (open > close)
            if (curr['open'] > curr['close'] and 
                prev1['open'] > prev1['close'] and 
                prev2['open'] > prev2['close']):
                
                # Close prices are decreasing
                if (curr['close'] < prev1['close'] and 
                    prev1['close'] < prev2['close']):
                    
                    # Body sizes (open - close) are increasing
                    curr_body = curr['open'] - curr['close']
                    prev1_body = prev1['open'] - prev1['close']
                    prev2_body = prev2['open'] - prev2['close']
                    
                    if (curr_body > prev1_body and prev1_body > prev2_body):
                        df.loc[df.index[i], 'euphoria_bullish'] = 1
            
            # Bearish Euphoria Pattern (bullish signal - three green candles)
            # All three candles are green (open < close)
            elif (curr['open'] < curr['close'] and 
                  prev1['open'] < prev1['close'] and 
                  prev2['open'] < prev2['close']):
                
                # Close prices are increasing
                if (curr['close'] > prev1['close'] and 
                    prev1['close'] > prev2['close']):
                    
                    # Body sizes: using (open - close) as in the original code
                    # For green candles, this is negative, but we check if it's becoming more negative
                    # (which means the body is getting larger)
                    curr_body_diff = curr['open'] - curr['close']
                    prev1_body_diff = prev1['open'] - prev1['close']
                    prev2_body_diff = prev2['open'] - prev2['close']
                    
                    # For green candles, (open - close) is negative
                    # More negative = larger body, so we check if curr < prev1 < prev2
                    if (curr_body_diff < prev1_body_diff and prev1_body_diff < prev2_body_diff):
                        df.loc[df.index[i], 'euphoria_bearish'] = 1
                        
        except (IndexError, KeyError):
            continue
    
    return df

# Detect Euphoria Pattern with K's Envelopes Signal
def detect_euphoria_with_k_envelopes(df, lookback=800):
    """
    Detect Euphoria patterns (using existing detection) and generate signals 
    only when price is inside K's envelopes.
    
    Euphoria is a contrarian signal:
    - Bullish Euphoria (three red candles) = contrarian bearish signal → BUY/LONG
    - Bearish Euphoria (three green candles) = contrarian bullish signal → SELL/SHORT
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    lookback : int
        Period for K's envelopes (default: 800)
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added signal columns
    """
    df = df.copy()
    
    # Calculate K's envelopes
    df = calculate_k_envelopes(df, lookback=lookback)
    
    # Use existing euphoria pattern detection
    df = detect_euphoria_pattern(df)
    
    # Initialize signal columns
    df['buy_signal'] = 0
    df['sell_signal'] = 0
    
    # Generate signals only when euphoria pattern is detected AND price is inside envelopes
    for i in range(len(df)):
        try:
            curr = df.iloc[i]
            
            # Check if we have valid envelope values
            if pd.isna(curr['k_envelope_upper']) or pd.isna(curr['k_envelope_lower']):
                continue
            
            # Bullish Euphoria (three red candles) = contrarian signal → BUY/LONG
            # This pattern suggests potential reversal UP
            if curr['euphoria_bullish'] == 1:
                # Check if price is inside K's envelopes at the time of pattern detection
                if (curr['close'] > curr['k_envelope_lower'] and 
                    curr['close'] < curr['k_envelope_upper']):
                    # Signal on next candle (i+1)
                    if i + 1 < len(df):
                        df.loc[df.index[i+1], 'buy_signal'] = 1
            
            # Bearish Euphoria (three green candles) = contrarian signal → SELL/SHORT
            # This pattern suggests potential reversal DOWN
            elif curr['euphoria_bearish'] == 1:
                # Check if price is inside K's envelopes at the time of pattern detection
                if (curr['close'] > curr['k_envelope_lower'] and 
                    curr['close'] < curr['k_envelope_upper']):
                    # Signal on next candle (i+1)
                    if i + 1 < len(df):
                        df.loc[df.index[i+1], 'sell_signal'] = -1
                        
        except (IndexError, KeyError):
            continue
    
    return df

# Detect Euphoria Pattern with K's Envelopes + Volume Confirmation
def detect_euphoria_with_volume_confirmation(df, lookback=800, vol_fast=20, vol_slow=50):
    """
    Detect Euphoria patterns with K's Envelopes and Volume Confirmation.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    lookback : int
        Period for K's envelopes (default: 800)
    vol_fast : int
        Fast volume MA period (default: 20)
    vol_slow : int
        Slow volume MA period (default: 50)
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added signal columns and volume confirmation
    """
    df = df.copy()
    
    # Calculate K's envelopes
    df = calculate_k_envelopes(df, lookback=lookback)
    
    # Calculate volume indicators
    df = calculate_volume_indicators(df, fast_period=vol_fast, slow_period=vol_slow)
    
    # Use existing euphoria pattern detection
    df = detect_euphoria_pattern(df)
    
    # Initialize signal columns
    df['buy_signal'] = 0
    df['sell_signal'] = 0
    df['buy_signal_confirmed'] = 0  # Volume confirmed
    df['sell_signal_confirmed'] = 0  # Volume confirmed
    df['volume_confirmation'] = ''  # Store confirmation details
    
    # Generate signals only when euphoria pattern is detected AND price is inside envelopes
    for i in range(len(df)):
        try:
            curr = df.iloc[i]
            
            # Check if we have valid envelope values
            if pd.isna(curr['k_envelope_upper']) or pd.isna(curr['k_envelope_lower']):
                continue
            
            # Bullish Euphoria (three red candles) = contrarian signal → BUY/LONG
            if curr['euphoria_bullish'] == 1:
                # Check if price is inside K's envelopes
                if (curr['close'] > curr['k_envelope_lower'] and 
                    curr['close'] < curr['k_envelope_upper']):
                    # Signal on next candle (i+1)
                    if i + 1 < len(df):
                        df.loc[df.index[i+1], 'buy_signal'] = 1
                        
                        # Check volume confirmation
                        vol_conf = check_volume_confirmation(df, i, 'bullish')
                        if vol_conf['confirmed']:
                            df.loc[df.index[i+1], 'buy_signal_confirmed'] = 1
                            df.loc[df.index[i+1], 'volume_confirmation'] = f"BUY: {vol_conf['conviction']}"
            
            # Bearish Euphoria (three green candles) = contrarian signal → SELL/SHORT
            elif curr['euphoria_bearish'] == 1:
                # Check if price is inside K's envelopes
                if (curr['close'] > curr['k_envelope_lower'] and 
                    curr['close'] < curr['k_envelope_upper']):
                    # Signal on next candle (i+1)
                    if i + 1 < len(df):
                        df.loc[df.index[i+1], 'sell_signal'] = -1
                        
                        # Check volume confirmation
                        vol_conf = check_volume_confirmation(df, i, 'bearish')
                        if vol_conf['confirmed']:
                            df.loc[df.index[i+1], 'sell_signal_confirmed'] = -1
                            df.loc[df.index[i+1], 'volume_confirmation'] = f"SELL: {vol_conf['conviction']}"
                        
        except (IndexError, KeyError):
            continue
    
    return df

# Detect Euphoria with Full Confluence (K's Envelopes + Volume + RSI + MACD + ADX)
def detect_euphoria_full_confluence(df, lookback=800, rsi_period=14, vol_fast=20, vol_slow=50, 
                                    macd_fast=12, macd_slow=26, macd_signal=9, adx_period=14):
    """
    Detect Euphoria patterns with full confluence: K's Envelopes + Volume + RSI + MACD + ADX.
    
    Signal Classification:
    - Highest Conviction: Euphoria + K's + Vol + RSI + MACD + ADX (all 4 confirmations)
    - High Conviction: Euphoria + K's + Vol + RSI + MACD (3 of 4)
    - Medium Conviction: Euphoria + K's + Vol + RSI (2 of 4)
    - Low Conviction: Euphoria + K's + Vol (1 of 4) or Euphoria + K's only (0 of 4)
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    lookback : int
        Period for K's envelopes
    rsi_period : int
        RSI period (default: 14)
    vol_fast : int
        Fast volume MA period
    vol_slow : int
        Slow volume MA period
    macd_fast : int
        MACD fast EMA period (default: 12)
    macd_slow : int
        MACD slow EMA period (default: 26)
    macd_signal : int
        MACD signal line EMA period (default: 9)
    adx_period : int
        ADX period (default: 14)
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added signal columns and confluence levels
    """
    df = df.copy()
    
    # Calculate all indicators
    df = calculate_k_envelopes(df, lookback=lookback)
    df = calculate_volume_indicators(df, fast_period=vol_fast, slow_period=vol_slow)
    df = calculate_rsi(df, period=rsi_period)
    df = detect_rsi_divergence(df)
    df = calculate_macd(df, fast_period=macd_fast, slow_period=macd_slow, signal_period=macd_signal)
    df = detect_macd_divergence(df)
    df = calculate_adx(df, period=adx_period)
    df = detect_euphoria_pattern(df)
    
    # Initialize signal columns
    df['buy_signal'] = 0
    df['sell_signal'] = 0
    df['buy_signal_highest'] = 0  # Highest conviction (all 4 confirmations)
    df['buy_signal_high'] = 0  # High conviction (3 of 4)
    df['buy_signal_medium'] = 0  # Medium conviction (2 of 4)
    df['buy_signal_low'] = 0  # Low conviction (envelopes only)
    df['sell_signal_highest'] = 0
    df['sell_signal_high'] = 0
    df['sell_signal_medium'] = 0
    df['sell_signal_low'] = 0
    df['confluence_details'] = ''  # Store confluence details
    
    # Generate signals with confluence checking
    for i in range(len(df)):
        try:
            curr = df.iloc[i]
            
            # Check if we have valid envelope values
            if pd.isna(curr['k_envelope_upper']) or pd.isna(curr['k_envelope_lower']):
                continue
            
            # Bullish Euphoria (three red candles) = contrarian signal → BUY/LONG
            if curr['euphoria_bullish'] == 1:
                # Check if price is inside K's envelopes
                if (curr['close'] > curr['k_envelope_lower'] and 
                    curr['close'] < curr['k_envelope_upper']):
                    # Signal on next candle (i+1)
                    if i + 1 < len(df):
                        df.loc[df.index[i+1], 'buy_signal'] = 1
                        
                        # Check all confirmations
                        vol_conf = check_volume_confirmation(df, i, 'bullish')
                        rsi_conf = check_rsi_confirmation(df, i, 'bullish')
                        macd_conf = check_macd_confirmation(df, i, 'bullish')
                        adx_conf = check_adx_confirmation(df, i, 'bullish')
                        
                        # Determine confluence level
                        has_volume = vol_conf['confirmed']
                        has_rsi = rsi_conf['confirmed']
                        has_macd = macd_conf['confirmed']
                        has_adx = adx_conf['confirmed']
                        
                        confluence_count = sum([has_volume, has_rsi, has_macd, has_adx])
                        
                        confluence_parts = []
                        if has_volume:
                            confluence_parts.append('Vol')
                        if has_rsi:
                            confluence_parts.append(f"RSI({rsi_conf['reason']})")
                        if has_macd:
                            confluence_parts.append(f"MACD({macd_conf['reason']})")
                        if has_adx:
                            confluence_parts.append(f"ADX({adx_conf['reason']})")
                        
                        # Classify by confluence count (all 4 = highest, 3 = high, 2 = medium, 1 or 0 = low)
                        if confluence_count == 4:
                            df.loc[df.index[i+1], 'buy_signal_highest'] = 1
                            confluence = 'Highest: ' + ' + '.join(confluence_parts)
                        elif confluence_count == 3:
                            df.loc[df.index[i+1], 'buy_signal_high'] = 1
                            confluence = 'High: ' + ' + '.join(confluence_parts)
                        elif confluence_count == 2:
                            df.loc[df.index[i+1], 'buy_signal_medium'] = 1
                            confluence = 'Medium: ' + ' + '.join(confluence_parts)
                        else:
                            df.loc[df.index[i+1], 'buy_signal_low'] = 1
                            confluence = 'Low: Envelopes only'
                        
                        df.loc[df.index[i+1], 'confluence_details'] = confluence
            
            # Bearish Euphoria (three green candles) = contrarian signal → SELL/SHORT
            elif curr['euphoria_bearish'] == 1:
                # Check if price is inside K's envelopes
                if (curr['close'] > curr['k_envelope_lower'] and 
                    curr['close'] < curr['k_envelope_upper']):
                    # Signal on next candle (i+1)
                    if i + 1 < len(df):
                        df.loc[df.index[i+1], 'sell_signal'] = -1
                        
                        # Check all confirmations
                        vol_conf = check_volume_confirmation(df, i, 'bearish')
                        rsi_conf = check_rsi_confirmation(df, i, 'bearish')
                        macd_conf = check_macd_confirmation(df, i, 'bearish')
                        adx_conf = check_adx_confirmation(df, i, 'bearish')
                        
                        # Determine confluence level
                        has_volume = vol_conf['confirmed']
                        has_rsi = rsi_conf['confirmed']
                        has_macd = macd_conf['confirmed']
                        has_adx = adx_conf['confirmed']
                        
                        confluence_count = sum([has_volume, has_rsi, has_macd, has_adx])
                        
                        confluence_parts = []
                        if has_volume:
                            confluence_parts.append('Vol')
                        if has_rsi:
                            confluence_parts.append(f"RSI({rsi_conf['reason']})")
                        if has_macd:
                            confluence_parts.append(f"MACD({macd_conf['reason']})")
                        if has_adx:
                            confluence_parts.append(f"ADX({adx_conf['reason']})")
                        
                        # Classify by confluence count (all 4 = highest, 3 = high, 2 = medium, 1 or 0 = low)
                        if confluence_count == 4:
                            df.loc[df.index[i+1], 'sell_signal_highest'] = -1
                            confluence = 'Highest: ' + ' + '.join(confluence_parts)
                        elif confluence_count == 3:
                            df.loc[df.index[i+1], 'sell_signal_high'] = -1
                            confluence = 'High: ' + ' + '.join(confluence_parts)
                        elif confluence_count == 2:
                            df.loc[df.index[i+1], 'sell_signal_medium'] = -1
                            confluence = 'Medium: ' + ' + '.join(confluence_parts)
                        else:
                            df.loc[df.index[i+1], 'sell_signal_low'] = -1
                            confluence = 'Low: Envelopes only'
                        
                        df.loc[df.index[i+1], 'confluence_details'] = confluence
                        
        except (IndexError, KeyError) as e:
            continue
    
    return df

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_atr(df, period=14):
    """
    Calculate Average True Range (ATR).
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    period : int
        ATR period (default: 14)
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'atr' column
    """
    df = df.copy()
    
    # Calculate True Range
    df['tr1'] = df['high'] - df['low']
    df['tr2'] = abs(df['high'] - df['close'].shift(1))
    df['tr3'] = abs(df['low'] - df['close'].shift(1))
    df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
    
    # Calculate ATR as moving average of TR
    df['atr'] = df['tr'].rolling(window=period).mean()
    
    # Clean up temporary columns
    df = df.drop(columns=['tr1', 'tr2', 'tr3', 'tr'])
    
    return df

def get_pattern_params(pattern_name):
    """
    Return default parameters for a pattern.
    
    Parameters:
    -----------
    pattern_name : str
        Name of the pattern
    
    Returns:
    --------
    dict
        Dictionary with default parameters for the pattern
    """
    params = {
        'marubozu': {},
        'three_candles': {'body': 0.0005},
        'three_methods': {},
        'tasuki': {},
        'hikkake': {},
        'quintuplets': {'body': 0.0003},
        'doji': {},
        'harami': {},
        'tweezers': {'body': 0.0003},
        'stick_sandwich': {},
        'hammer': {'body': 0.0003, 'wick': 0.0005},
        'star': {},
        'piercing': {},
        'engulfing': {},
        'abandoned_baby': {},
        'spinning_top': {'body': 0.0003, 'wick': 0.0003},
        'inside_up_down': {'body': 0.0003},
        'tower': {'body': 0.0003},
        'on_neck': {},
        'double_trouble': {'atr_period': 14},
        'bottle': {},
        'slingshot': {},
        'h_pattern': {},
        'doppelganger': {},
        'blockade': {},
        'barrier': {},
        'mirror': {},
        'shrinking': {},
        'euphoria': {}
    }
    return params.get(pattern_name.lower(), {})

def list_all_patterns():
    """
    Return list of all available patterns with descriptions.
    
    Returns:
    --------
    list
        List of dictionaries with pattern information
    """
    patterns = [
        {'name': 'marubozu', 'category': 'Trend-Following', 'description': 'Single candle with no wicks'},
        {'name': 'three_candles', 'category': 'Trend-Following', 'description': 'Three consecutive large candles'},
        {'name': 'three_methods', 'category': 'Trend-Following', 'description': 'Five-candle continuation pattern'},
        {'name': 'tasuki', 'category': 'Trend-Following', 'description': 'Three-candle gap continuation'},
        {'name': 'hikkake', 'category': 'Trend-Following', 'description': 'Five-candle false breakout pattern'},
        {'name': 'quintuplets', 'category': 'Trend-Following', 'description': 'Five consecutive small candles'},
        {'name': 'doji', 'category': 'Classic Contrarian', 'description': 'Single candle with open = close'},
        {'name': 'harami', 'category': 'Classic Contrarian', 'description': 'Two-candle reversal pattern'},
        {'name': 'tweezers', 'category': 'Classic Contrarian', 'description': 'Two candles with same high/low'},
        {'name': 'stick_sandwich', 'category': 'Classic Contrarian', 'description': 'Three-candle sandwich pattern'},
        {'name': 'hammer', 'category': 'Classic Contrarian', 'description': 'Single candle with long lower shadow'},
        {'name': 'star', 'category': 'Classic Contrarian', 'description': 'Three-candle star pattern'},
        {'name': 'piercing', 'category': 'Classic Contrarian', 'description': 'Two-candle bullish reversal'},
        {'name': 'engulfing', 'category': 'Classic Contrarian', 'description': 'Two-candle engulfing reversal'},
        {'name': 'abandoned_baby', 'category': 'Classic Contrarian', 'description': 'Three-candle reversal with gaps'},
        {'name': 'spinning_top', 'category': 'Classic Contrarian', 'description': 'Three-candle indecision pattern'},
        {'name': 'inside_up_down', 'category': 'Classic Contrarian', 'description': 'Three-candle inside bar reversal'},
        {'name': 'tower', 'category': 'Classic Contrarian', 'description': 'Five-candle stabilization pattern'},
        {'name': 'on_neck', 'category': 'Classic Contrarian', 'description': 'Two-candle same close pattern'},
        {'name': 'double_trouble', 'category': 'Modern Trend-Following', 'description': 'Two-candle ATR-validated pattern'},
        {'name': 'bottle', 'category': 'Modern Trend-Following', 'description': 'Two-candle continuation pattern'},
        {'name': 'slingshot', 'category': 'Modern Trend-Following', 'description': 'Four-candle breakout pattern'},
        {'name': 'h_pattern', 'category': 'Modern Trend-Following', 'description': 'Three-candle Doji continuation'},
        {'name': 'doppelganger', 'category': 'Modern Contrarian', 'description': 'Three-candle twin candles pattern'},
        {'name': 'blockade', 'category': 'Modern Contrarian', 'description': 'Four-candle stabilization pattern'},
        {'name': 'barrier', 'category': 'Modern Contrarian', 'description': 'Three-candle same support/resistance'},
        {'name': 'mirror', 'category': 'Modern Contrarian', 'description': 'Four-candle U-turn reversal'},
        {'name': 'shrinking', 'category': 'Modern Contrarian', 'description': 'Five-candle compression pattern'},
        {'name': 'euphoria', 'category': 'Modern Contrarian', 'description': 'Three-candle exhaustion pattern'}
    ]
    return patterns

def detect_pattern_by_name(df, pattern_name, **kwargs):
    """
    Generic pattern detector that routes to specific pattern function.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    pattern_name : str
        Name of the pattern to detect
    **kwargs : dict
        Pattern-specific parameters
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with pattern detection columns added
    """
    pattern_name = pattern_name.lower()
    
    pattern_functions = {
        'marubozu': detect_marubozu,
        'three_candles': detect_three_candles,
        'three_methods': detect_three_methods,
        'tasuki': detect_tasuki,
        'hikkake': detect_hikkake,
        'quintuplets': detect_quintuplets,
        'doji': detect_doji,
        'harami': detect_harami,
        'tweezers': detect_tweezers,
        'stick_sandwich': detect_stick_sandwich,
        'hammer': detect_hammer,
        'star': detect_star,
        'piercing': detect_piercing,
        'engulfing': detect_engulfing,
        'abandoned_baby': detect_abandoned_baby,
        'spinning_top': detect_spinning_top,
        'inside_up_down': detect_inside_up_down,
        'tower': detect_tower,
        'on_neck': detect_on_neck,
        'double_trouble': detect_double_trouble,
        'bottle': detect_bottle,
        'slingshot': detect_slingshot,
        'h_pattern': detect_h_pattern,
        'doppelganger': detect_doppelganger,
        'blockade': detect_blockade,
        'barrier': detect_barrier,
        'mirror': detect_mirror,
        'shrinking': detect_shrinking,
        'euphoria': detect_euphoria_pattern
    }
    
    if pattern_name not in pattern_functions:
        raise ValueError(f"Unknown pattern: {pattern_name}. Available patterns: {list(pattern_functions.keys())}")
    
    return pattern_functions[pattern_name](df, **kwargs)

# ============================================================================
# TREND-FOLLOWING PATTERNS
# ============================================================================

def detect_marubozu(df):
    """
    Detect Marubozu pattern.
    
    A single-candle pattern with no wicks (shadows), indicating strong momentum.
    Bullish: open = low and close = high
    Bearish: open = high and close = low
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'marubozu_bullish' and 'marubozu_bearish' columns
    """
    df = df.copy()
    df['marubozu_bullish'] = 0
    df['marubozu_bearish'] = 0
    
    for i in range(len(df)):
        try:
            # Bullish Marubozu: open == low AND close == high
            if (df.iloc[i]['close'] > df.iloc[i]['open'] and
                df.iloc[i]['high'] == df.iloc[i]['close'] and
                df.iloc[i]['low'] == df.iloc[i]['open']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'marubozu_bullish'] = 1
            
            # Bearish Marubozu: open == high AND close == low
            elif (df.iloc[i]['close'] < df.iloc[i]['open'] and
                  df.iloc[i]['high'] == df.iloc[i]['open'] and
                  df.iloc[i]['low'] == df.iloc[i]['close']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'marubozu_bearish'] = 1
        except (IndexError, KeyError):
            continue
    
    return df

def detect_three_candles(df, body=0.0005):
    """
    Detect Three Candles pattern (Three White Soldiers / Three Black Crows).
    
    Three consecutive large candles of the same color, each closing higher/lower than the previous.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    body : float
        Minimum body size threshold (default: 0.0005)
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'three_candles_bullish' and 'three_candles_bearish' columns
    """
    df = df.copy()
    df['three_candles_bullish'] = 0
    df['three_candles_bearish'] = 0
    
    for i in range(3, len(df)):
        try:
            # Bullish: Three consecutive bullish candles with body > threshold
            if (df.iloc[i]['close'] - df.iloc[i]['open'] > body and
                df.iloc[i-1]['close'] - df.iloc[i-1]['open'] > body and
                df.iloc[i-2]['close'] - df.iloc[i-2]['open'] > body and
                df.iloc[i]['close'] > df.iloc[i-1]['close'] and
                df.iloc[i-1]['close'] > df.iloc[i-2]['close'] and
                df.iloc[i-2]['close'] > df.iloc[i-3]['close']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'three_candles_bullish'] = 1
            
            # Bearish: Three consecutive bearish candles
            elif (df.iloc[i]['open'] - df.iloc[i]['close'] > body and
                  df.iloc[i-1]['open'] - df.iloc[i-1]['close'] > body and
                  df.iloc[i-2]['open'] - df.iloc[i-2]['close'] > body and
                  df.iloc[i]['close'] < df.iloc[i-1]['close'] and
                  df.iloc[i-1]['close'] < df.iloc[i-2]['close'] and
                  df.iloc[i-2]['close'] < df.iloc[i-3]['close']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'three_candles_bearish'] = 1
        except (IndexError, KeyError):
            continue
    
    return df

def detect_three_methods(df):
    """
    Detect Three Methods pattern.
    
    Rising Three Methods: large bullish candle → three small bearish candles contained within the first → large bullish candle breaking out.
    Falling Three Methods is the bearish mirror.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'three_methods_bullish' and 'three_methods_bearish' columns
    """
    df = df.copy()
    df['three_methods_bullish'] = 0
    df['three_methods_bearish'] = 0
    
    for i in range(4, len(df)):
        try:
            # Rising Three Methods
            if (df.iloc[i]['close'] > df.iloc[i]['open'] and
                df.iloc[i]['close'] > df.iloc[i-4]['high'] and
                df.iloc[i]['low'] < df.iloc[i-1]['low'] and
                df.iloc[i-1]['close'] < df.iloc[i-4]['close'] and
                df.iloc[i-1]['low'] > df.iloc[i-4]['low'] and
                df.iloc[i-2]['close'] < df.iloc[i-4]['close'] and
                df.iloc[i-2]['low'] > df.iloc[i-4]['low'] and
                df.iloc[i-3]['close'] < df.iloc[i-4]['close'] and
                df.iloc[i-3]['low'] > df.iloc[i-4]['low'] and
                df.iloc[i-4]['close'] > df.iloc[i-4]['open']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'three_methods_bullish'] = 1
            
            # Falling Three Methods
            elif (df.iloc[i]['close'] < df.iloc[i]['open'] and
                  df.iloc[i]['close'] < df.iloc[i-4]['low'] and
                  df.iloc[i]['high'] > df.iloc[i-1]['high'] and
                  df.iloc[i-1]['close'] > df.iloc[i-4]['close'] and
                  df.iloc[i-1]['high'] < df.iloc[i-4]['high'] and
                  df.iloc[i-2]['close'] > df.iloc[i-4]['close'] and
                  df.iloc[i-2]['high'] < df.iloc[i-4]['high'] and
                  df.iloc[i-3]['close'] > df.iloc[i-4]['close'] and
                  df.iloc[i-3]['high'] < df.iloc[i-4]['high'] and
                  df.iloc[i-4]['close'] < df.iloc[i-4]['open']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'three_methods_bearish'] = 1
        except (IndexError, KeyError):
            continue
    
    return df

def detect_tasuki(df):
    """
    Detect Tasuki pattern.
    
    A three-candle gap continuation pattern. Bullish: bearish candle → bullish candle gapping up → bearish candle closing within the gap.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'tasuki_bullish' and 'tasuki_bearish' columns
    """
    df = df.copy()
    df['tasuki_bullish'] = 0
    df['tasuki_bearish'] = 0
    
    for i in range(2, len(df)):
        try:
            # Bullish Tasuki
            if (df.iloc[i]['close'] < df.iloc[i]['open'] and
                df.iloc[i]['close'] < df.iloc[i-1]['open'] and
                df.iloc[i]['close'] > df.iloc[i-2]['close'] and
                df.iloc[i-1]['close'] > df.iloc[i-1]['open'] and
                df.iloc[i-1]['open'] > df.iloc[i-2]['close'] and
                df.iloc[i-2]['close'] > df.iloc[i-2]['open']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'tasuki_bullish'] = 1
            
            # Bearish Tasuki
            elif (df.iloc[i]['close'] > df.iloc[i]['open'] and
                  df.iloc[i]['close'] > df.iloc[i-1]['open'] and
                  df.iloc[i]['close'] < df.iloc[i-2]['close'] and
                  df.iloc[i-1]['close'] < df.iloc[i-1]['open'] and
                  df.iloc[i-1]['open'] < df.iloc[i-2]['close'] and
                  df.iloc[i-2]['close'] < df.iloc[i-2]['open']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'tasuki_bearish'] = 1
        except (IndexError, KeyError):
            continue
    
    return df

def detect_hikkake(df):
    """
    Detect Hikkake pattern.
    
    A five-candle pattern featuring a false breakout. Bullish: starts with bullish candle → bearish candle embedded inside → two bearish candles breaking below → breakout above validates.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'hikkake_bullish' and 'hikkake_bearish' columns
    """
    df = df.copy()
    df['hikkake_bullish'] = 0
    df['hikkake_bearish'] = 0
    
    for i in range(4, len(df)):
        try:
            # Bullish Hikkake
            if (df.iloc[i]['close'] > df.iloc[i-3]['high'] and
                df.iloc[i]['close'] > df.iloc[i-4]['close'] and
                df.iloc[i-1]['low'] < df.iloc[i]['open'] and
                df.iloc[i-1]['close'] < df.iloc[i]['close'] and
                df.iloc[i-1]['high'] <= df.iloc[i-3]['high'] and
                df.iloc[i-2]['low'] < df.iloc[i]['open'] and
                df.iloc[i-2]['close'] < df.iloc[i]['close'] and
                df.iloc[i-2]['high'] <= df.iloc[i-3]['high'] and
                df.iloc[i-3]['high'] < df.iloc[i-4]['high'] and
                df.iloc[i-3]['low'] > df.iloc[i-4]['low'] and
                df.iloc[i-4]['close'] > df.iloc[i-4]['open']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'hikkake_bullish'] = 1
            
            # Bearish Hikkake
            elif (df.iloc[i]['close'] < df.iloc[i-3]['low'] and
                  df.iloc[i]['close'] < df.iloc[i-4]['close'] and
                  df.iloc[i-1]['high'] > df.iloc[i]['open'] and
                  df.iloc[i-1]['close'] > df.iloc[i]['close'] and
                  df.iloc[i-1]['low'] >= df.iloc[i-3]['low'] and
                  df.iloc[i-2]['high'] > df.iloc[i]['open'] and
                  df.iloc[i-2]['close'] > df.iloc[i]['close'] and
                  df.iloc[i-2]['low'] >= df.iloc[i-3]['low'] and
                  df.iloc[i-3]['low'] > df.iloc[i-4]['low'] and
                  df.iloc[i-3]['high'] < df.iloc[i-4]['high'] and
                  df.iloc[i-4]['close'] < df.iloc[i-4]['open']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'hikkake_bearish'] = 1
        except (IndexError, KeyError):
            continue
    
    return df

def detect_quintuplets(df, body=0.0003):
    """
    Detect Quintuplets pattern.
    
    Five consecutive small candles in the same direction, each closing progressively higher (bullish) or lower (bearish).
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    body : float
        Maximum body size threshold (default: 0.0003)
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'quintuplets_bullish' and 'quintuplets_bearish' columns
    """
    df = df.copy()
    df['quintuplets_bullish'] = 0
    df['quintuplets_bearish'] = 0
    
    for i in range(4, len(df)):
        try:
            # Bullish: 5 small bullish candles, each close > previous close
            if (df.iloc[i]['close'] > df.iloc[i]['open'] and
                df.iloc[i]['close'] - df.iloc[i]['open'] < body and
                df.iloc[i]['close'] > df.iloc[i-1]['close'] and
                df.iloc[i-1]['close'] > df.iloc[i-1]['open'] and
                df.iloc[i-1]['close'] - df.iloc[i-1]['open'] < body and
                df.iloc[i-1]['close'] > df.iloc[i-2]['close'] and
                df.iloc[i-2]['close'] > df.iloc[i-2]['open'] and
                df.iloc[i-2]['close'] - df.iloc[i-2]['open'] < body and
                df.iloc[i-2]['close'] > df.iloc[i-3]['close'] and
                df.iloc[i-3]['close'] > df.iloc[i-3]['open'] and
                df.iloc[i-3]['close'] - df.iloc[i-3]['open'] < body and
                df.iloc[i-3]['close'] > df.iloc[i-4]['close'] and
                df.iloc[i-4]['close'] > df.iloc[i-4]['open'] and
                df.iloc[i-4]['close'] - df.iloc[i-4]['open'] < body):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'quintuplets_bullish'] = 1
            
            # Bearish: 5 small bearish candles
            elif (df.iloc[i]['close'] < df.iloc[i]['open'] and
                  df.iloc[i]['open'] - df.iloc[i]['close'] < body and
                  df.iloc[i]['close'] < df.iloc[i-1]['close'] and
                  df.iloc[i-1]['close'] < df.iloc[i-1]['open'] and
                  df.iloc[i-1]['open'] - df.iloc[i-1]['close'] < body and
                  df.iloc[i-1]['close'] < df.iloc[i-2]['close'] and
                  df.iloc[i-2]['close'] < df.iloc[i-2]['open'] and
                  df.iloc[i-2]['open'] - df.iloc[i-2]['close'] < body and
                  df.iloc[i-2]['close'] < df.iloc[i-3]['close'] and
                  df.iloc[i-3]['close'] < df.iloc[i-3]['open'] and
                  df.iloc[i-3]['open'] - df.iloc[i-3]['close'] < body and
                  df.iloc[i-3]['close'] < df.iloc[i-4]['close'] and
                  df.iloc[i-4]['close'] < df.iloc[i-4]['open'] and
                  df.iloc[i-4]['open'] - df.iloc[i-4]['close'] < body):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'quintuplets_bearish'] = 1
        except (IndexError, KeyError):
            continue
    
    return df

# ============================================================================
# CLASSIC CONTRARIAN PATTERNS
# ============================================================================

def detect_doji(df):
    """
    Detect Doji pattern.
    
    A single candle where open = close (or very close), creating a cross-like shape.
    Signals indecision and potential reversal.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'doji_bullish' and 'doji_bearish' columns
    """
    df = df.copy()
    df['doji_bullish'] = 0
    df['doji_bearish'] = 0
    
    for i in range(2, len(df)):
        try:
            # Bullish Doji: Doji after downtrend, confirmed by bullish candle
            if (df.iloc[i]['close'] > df.iloc[i]['open'] and
                df.iloc[i]['close'] > df.iloc[i-1]['close'] and
                df.iloc[i-1]['close'] == df.iloc[i-1]['open'] and  # Doji
                df.iloc[i-2]['close'] < df.iloc[i-2]['open']):     # Prior bearish
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'doji_bullish'] = 1
            
            # Bearish Doji: Doji after uptrend, confirmed by bearish candle
            elif (df.iloc[i]['close'] < df.iloc[i]['open'] and
                  df.iloc[i]['close'] < df.iloc[i-1]['close'] and
                  df.iloc[i-1]['close'] == df.iloc[i-1]['open'] and  # Doji
                  df.iloc[i-2]['close'] > df.iloc[i-2]['open']):     # Prior bullish
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'doji_bearish'] = 1
        except (IndexError, KeyError):
            continue
    
    return df

def detect_harami(df):
    """
    Detect Harami pattern.
    
    A two-candle reversal pattern where the second candle's body is completely contained within the first candle's body.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'harami_bullish' and 'harami_bearish' columns
    """
    df = df.copy()
    df['harami_bullish'] = 0
    df['harami_bearish'] = 0
    
    for i in range(2, len(df)):
        try:
            # Bullish Harami: bearish mother → small bullish baby inside
            if (df.iloc[i]['close'] < df.iloc[i-1]['open'] and
                df.iloc[i]['open'] > df.iloc[i-1]['close'] and
                df.iloc[i]['high'] < df.iloc[i-1]['high'] and
                df.iloc[i]['low'] > df.iloc[i-1]['low'] and
                df.iloc[i]['close'] > df.iloc[i]['open'] and
                df.iloc[i-1]['close'] < df.iloc[i-1]['open'] and
                df.iloc[i-2]['close'] < df.iloc[i-2]['open']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'harami_bullish'] = 1
            
            # Bearish Harami: bullish mother → small bearish baby inside
            elif (df.iloc[i]['close'] > df.iloc[i-1]['open'] and
                  df.iloc[i]['open'] < df.iloc[i-1]['close'] and
                  df.iloc[i]['high'] < df.iloc[i-1]['high'] and
                  df.iloc[i]['low'] > df.iloc[i-1]['low'] and
                  df.iloc[i]['close'] < df.iloc[i]['open'] and
                  df.iloc[i-1]['close'] > df.iloc[i-1]['open'] and
                  df.iloc[i-2]['close'] > df.iloc[i-2]['open']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'harami_bearish'] = 1
        except (IndexError, KeyError):
            continue
    
    return df

def detect_tweezers(df, body=0.0003):
    """
    Detect Tweezers pattern.
    
    A two-candle pattern where consecutive candles share the same low (bullish Tweezers Bottom) or same high (bearish Tweezers Top).
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    body : float
        Maximum body size for small candle (default: 0.0003)
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'tweezers_bullish' and 'tweezers_bearish' columns
    """
    df = df.copy()
    df = df.round(decimals=4)  # Round for exact price matching
    df['tweezers_bullish'] = 0
    df['tweezers_bearish'] = 0
    
    for i in range(2, len(df)):
        try:
            # Bullish Tweezers: same low, bullish candle after bearish
            if (df.iloc[i]['close'] > df.iloc[i]['open'] and
                df.iloc[i]['low'] == df.iloc[i-1]['low'] and
                df.iloc[i]['close'] - df.iloc[i]['open'] < body and
                df.iloc[i-1]['close'] < df.iloc[i-1]['open'] and
                df.iloc[i-2]['close'] < df.iloc[i-2]['open']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'tweezers_bullish'] = 1
            
            # Bearish Tweezers: same high, bearish candle after bullish
            elif (df.iloc[i]['close'] < df.iloc[i]['open'] and
                  df.iloc[i]['high'] == df.iloc[i-1]['high'] and
                  df.iloc[i-1]['close'] > df.iloc[i-1]['open'] and
                  df.iloc[i-2]['close'] > df.iloc[i-2]['open']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'tweezers_bearish'] = 1
        except (IndexError, KeyError):
            continue
    
    return df

def detect_stick_sandwich(df):
    """
    Detect Stick Sandwich pattern.
    
    A three-candle pattern with two same-color outer candles "sandwiching" an opposite-color middle candle.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'stick_sandwich_bullish' and 'stick_sandwich_bearish' columns
    """
    df = df.copy()
    df['stick_sandwich_bullish'] = 0
    df['stick_sandwich_bearish'] = 0
    
    for i in range(3, len(df)):
        try:
            # Bullish Stick Sandwich
            if (df.iloc[i]['close'] < df.iloc[i]['open'] and
                df.iloc[i]['high'] > df.iloc[i-1]['high'] and
                df.iloc[i]['low'] < df.iloc[i-1]['low'] and
                df.iloc[i-1]['close'] > df.iloc[i-1]['open'] and
                df.iloc[i-2]['close'] < df.iloc[i-2]['open'] and
                df.iloc[i-2]['high'] > df.iloc[i-1]['high'] and
                df.iloc[i-2]['low'] < df.iloc[i-1]['low'] and
                df.iloc[i-2]['close'] < df.iloc[i-3]['close'] and
                df.iloc[i-3]['close'] < df.iloc[i-3]['open']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'stick_sandwich_bullish'] = 1
            
            # Bearish Stick Sandwich
            elif (df.iloc[i]['close'] > df.iloc[i]['open'] and
                  df.iloc[i]['high'] > df.iloc[i-1]['high'] and
                  df.iloc[i]['low'] < df.iloc[i-1]['low'] and
                  df.iloc[i-1]['close'] < df.iloc[i-1]['open'] and
                  df.iloc[i-2]['close'] > df.iloc[i-2]['open'] and
                  df.iloc[i-2]['high'] > df.iloc[i-1]['high'] and
                  df.iloc[i-2]['low'] < df.iloc[i-1]['low']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'stick_sandwich_bearish'] = 1
        except (IndexError, KeyError):
            continue
    
    return df

def detect_hammer(df, body=0.0003, wick=0.0005):
    """
    Detect Hammer pattern.
    
    A single candle with a small body near the top and a long lower shadow (at least 2x the body).
    No or minimal upper shadow. Signals potential reversal when appearing after a downtrend.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    body : float
        Maximum body size (default: 0.0003)
    wick : float
        Minimum wick size (default: 0.0005)
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'hammer_bullish' and 'hammer_bearish' columns
    """
    df = df.copy()
    df['hammer_bullish'] = 0
    df['hammer_bearish'] = 0
    
    for i in range(2, len(df)):
        try:
            # Bullish Hammer: small body, long lower wick, close == high
            if (df.iloc[i]['close'] > df.iloc[i]['open'] and
                abs(df.iloc[i-1]['close'] - df.iloc[i-1]['open']) < body and
                min(df.iloc[i-1]['close'], df.iloc[i-1]['open']) - df.iloc[i-1]['low'] > 2 * wick and
                df.iloc[i-1]['close'] == df.iloc[i-1]['high'] and
                df.iloc[i-2]['close'] < df.iloc[i-2]['open']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'hammer_bullish'] = 1
            
            # Bearish Hammer (Inverted): small body, long upper wick
            elif (df.iloc[i]['close'] < df.iloc[i]['open'] and
                  abs(df.iloc[i-1]['close'] - df.iloc[i-1]['open']) < body and
                  df.iloc[i-1]['high'] - max(df.iloc[i-1]['close'], df.iloc[i-1]['open']) > 2 * wick and
                  df.iloc[i-1]['close'] == df.iloc[i-1]['low'] and
                  df.iloc[i-2]['close'] > df.iloc[i-2]['open']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'hammer_bearish'] = 1
        except (IndexError, KeyError):
            continue
    
    return df

def detect_star(df):
    """
    Detect Star pattern (Morning Star / Evening Star).
    
    Morning Star (bullish): bearish candle → small gapped-down candle → bullish candle.
    Evening Star (bearish): bullish candle → small gapped-up candle → bearish candle.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'star_bullish' and 'star_bearish' columns
    """
    df = df.copy()
    df['star_bullish'] = 0
    df['star_bearish'] = 0
    
    for i in range(2, len(df)):
        try:
            # Morning Star
            if (df.iloc[i]['close'] > df.iloc[i]['open'] and
                max(df.iloc[i-1]['close'], df.iloc[i-1]['open']) < df.iloc[i]['open'] and
                max(df.iloc[i-1]['close'], df.iloc[i-1]['open']) < df.iloc[i-2]['close'] and
                df.iloc[i-2]['close'] < df.iloc[i-2]['open']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'star_bullish'] = 1
            
            # Evening Star
            elif (df.iloc[i]['close'] < df.iloc[i]['open'] and
                  min(df.iloc[i-1]['close'], df.iloc[i-1]['open']) > df.iloc[i]['open'] and
                  min(df.iloc[i-1]['close'], df.iloc[i-1]['open']) > df.iloc[i-2]['close'] and
                  df.iloc[i-2]['close'] > df.iloc[i-2]['open']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'star_bearish'] = 1
        except (IndexError, KeyError):
            continue
    
    return df

def detect_piercing(df):
    """
    Detect Piercing pattern (and Dark Cloud Cover).
    
    A two-candle bullish reversal. First candle is bearish, second is bullish that opens below the first's close
    but closes above the midpoint of the first candle (but not above its open).
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'piercing_bullish' and 'piercing_bearish' columns
    """
    df = df.copy()
    df['piercing_bullish'] = 0
    df['piercing_bearish'] = 0
    
    for i in range(2, len(df)):
        try:
            # Bullish Piercing
            if (df.iloc[i]['close'] > df.iloc[i]['open'] and
                df.iloc[i]['close'] < df.iloc[i-1]['open'] and
                df.iloc[i]['close'] > df.iloc[i-1]['close'] and
                df.iloc[i]['open'] < df.iloc[i-1]['close'] and
                df.iloc[i-1]['close'] < df.iloc[i-1]['open'] and
                df.iloc[i-2]['close'] < df.iloc[i-2]['open']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'piercing_bullish'] = 1
            
            # Bearish Dark Cloud Cover
            elif (df.iloc[i]['close'] < df.iloc[i]['open'] and
                  df.iloc[i]['close'] > df.iloc[i-1]['open'] and
                  df.iloc[i]['close'] < df.iloc[i-1]['close'] and
                  df.iloc[i]['open'] > df.iloc[i-1]['close'] and
                  df.iloc[i-1]['close'] > df.iloc[i-1]['open'] and
                  df.iloc[i-2]['close'] > df.iloc[i-2]['open']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'piercing_bearish'] = 1
        except (IndexError, KeyError):
            continue
    
    return df

def detect_engulfing(df):
    """
    Detect Engulfing pattern.
    
    A two-candle reversal pattern where the second candle's body completely engulfs the first candle's body.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'engulfing_bullish' and 'engulfing_bearish' columns
    """
    df = df.copy()
    df['engulfing_bullish'] = 0
    df['engulfing_bearish'] = 0
    
    for i in range(2, len(df)):
        try:
            # Bullish Engulfing
            if (df.iloc[i]['close'] > df.iloc[i]['open'] and
                df.iloc[i]['open'] < df.iloc[i-1]['close'] and
                df.iloc[i]['close'] > df.iloc[i-1]['open'] and
                df.iloc[i-1]['close'] < df.iloc[i-1]['open'] and
                df.iloc[i-2]['close'] < df.iloc[i-2]['open']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'engulfing_bullish'] = 1
            
            # Bearish Engulfing
            elif (df.iloc[i]['close'] < df.iloc[i]['open'] and
                  df.iloc[i]['open'] > df.iloc[i-1]['close'] and
                  df.iloc[i]['close'] < df.iloc[i-1]['open'] and
                  df.iloc[i-1]['close'] > df.iloc[i-1]['open'] and
                  df.iloc[i-2]['close'] > df.iloc[i-2]['open']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'engulfing_bearish'] = 1
        except (IndexError, KeyError):
            continue
    
    return df

def detect_abandoned_baby(df):
    """
    Detect Abandoned Baby pattern.
    
    A rare three-candle reversal pattern. Bullish: bearish candle → Doji that gaps below (no overlap) → bullish candle that gaps above the Doji.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'abandoned_baby_bullish' and 'abandoned_baby_bearish' columns
    """
    df = df.copy()
    df['abandoned_baby_bullish'] = 0
    df['abandoned_baby_bearish'] = 0
    
    for i in range(2, len(df)):
        try:
            # Bullish Abandoned Baby
            if (df.iloc[i]['close'] > df.iloc[i]['open'] and
                df.iloc[i-1]['close'] == df.iloc[i-1]['open'] and  # Doji
                df.iloc[i-1]['high'] < df.iloc[i]['low'] and       # Gap up from Doji
                df.iloc[i-1]['high'] < df.iloc[i-2]['low'] and     # Gap down to Doji
                df.iloc[i-2]['close'] < df.iloc[i-2]['open']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'abandoned_baby_bullish'] = 1
            
            # Bearish Abandoned Baby
            elif (df.iloc[i]['close'] < df.iloc[i]['open'] and
                  df.iloc[i-1]['close'] == df.iloc[i-1]['open'] and  # Doji
                  df.iloc[i-1]['low'] > df.iloc[i]['high'] and       # Gap down from Doji
                  df.iloc[i-1]['low'] > df.iloc[i-2]['high'] and     # Gap up to Doji
                  df.iloc[i-2]['close'] > df.iloc[i-2]['open']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'abandoned_baby_bearish'] = 1
        except (IndexError, KeyError):
            continue
    
    return df

def detect_spinning_top(df, body=0.0003, wick=0.0003):
    """
    Detect Spinning Top pattern.
    
    A three-candle reversal similar to Doji but more common. Features a small body with wicks on both sides, followed by confirmation.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    body : float
        Maximum body size (default: 0.0003)
    wick : float
        Minimum wick size (default: 0.0003)
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'spinning_top_bullish' and 'spinning_top_bearish' columns
    """
    df = df.copy()
    df['spinning_top_bullish'] = 0
    df['spinning_top_bearish'] = 0
    
    for i in range(2, len(df)):
        try:
            # Bullish Spinning Top (after bearish trend, confirmed by bullish)
            if (df.iloc[i]['close'] - df.iloc[i]['open'] > body and
                df.iloc[i-1]['high'] - df.iloc[i-1]['close'] >= wick and
                df.iloc[i-1]['open'] - df.iloc[i-1]['low'] >= wick and
                df.iloc[i-1]['close'] - df.iloc[i-1]['open'] < body and
                df.iloc[i-1]['close'] > df.iloc[i-1]['open'] and
                df.iloc[i-2]['close'] < df.iloc[i-2]['open'] and
                df.iloc[i-2]['open'] - df.iloc[i-2]['close'] > body):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'spinning_top_bullish'] = 1
            
            # Bearish Spinning Top
            elif (df.iloc[i]['open'] - df.iloc[i]['close'] > body and
                  df.iloc[i-1]['high'] - df.iloc[i-1]['open'] >= wick and
                  df.iloc[i-1]['close'] - df.iloc[i-1]['low'] >= wick and
                  df.iloc[i-1]['open'] - df.iloc[i-1]['close'] < body and
                  df.iloc[i-1]['close'] < df.iloc[i-1]['open'] and
                  df.iloc[i-2]['close'] > df.iloc[i-2]['open']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'spinning_top_bearish'] = 1
        except (IndexError, KeyError):
            continue
    
    return df

def detect_inside_up_down(df, body=0.0003):
    """
    Detect Inside Up/Down pattern.
    
    A three-candle reversal pattern. Inside Up (bullish): bearish candle → smaller bullish candle inside → bullish confirmation breaking above the first.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    body : float
        Minimum body size (default: 0.0003)
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'inside_up_down_bullish' and 'inside_up_down_bearish' columns
    """
    df = df.copy()
    df['inside_up_down_bullish'] = 0
    df['inside_up_down_bearish'] = 0
    
    for i in range(2, len(df)):
        try:
            # Inside Up (Bullish)
            if (df.iloc[i-2]['close'] < df.iloc[i-2]['open'] and
                abs(df.iloc[i-2]['open'] - df.iloc[i-2]['close']) > body and
                df.iloc[i-1]['close'] < df.iloc[i-2]['open'] and
                df.iloc[i-1]['open'] > df.iloc[i-2]['close'] and
                df.iloc[i-1]['close'] > df.iloc[i-1]['open'] and
                df.iloc[i]['close'] > df.iloc[i-2]['open'] and
                df.iloc[i]['close'] > df.iloc[i]['open'] and
                abs(df.iloc[i]['open'] - df.iloc[i]['close']) > body):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'inside_up_down_bullish'] = 1
            
            # Inside Down (Bearish)
            elif (df.iloc[i-2]['close'] > df.iloc[i-2]['open'] and
                  abs(df.iloc[i-2]['close'] - df.iloc[i-2]['open']) > body and
                  df.iloc[i-1]['close'] > df.iloc[i-2]['open'] and
                  df.iloc[i-1]['open'] < df.iloc[i-2]['close'] and
                  df.iloc[i-1]['close'] < df.iloc[i-1]['open'] and
                  df.iloc[i]['close'] < df.iloc[i-2]['open'] and
                  df.iloc[i]['close'] < df.iloc[i]['open'] and
                  abs(df.iloc[i]['open'] - df.iloc[i]['close']) > body):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'inside_up_down_bearish'] = 1
        except (IndexError, KeyError):
            continue
    
    return df

def detect_tower(df, body=0.0003):
    """
    Detect Tower pattern.
    
    A five-candle stabilization/reversal pattern. Tower Bottom: bearish candle → three small range-bound candles → bullish confirmation.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    body : float
        Minimum body size (default: 0.0003)
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'tower_bullish' and 'tower_bearish' columns
    """
    df = df.copy()
    df['tower_bullish'] = 0
    df['tower_bearish'] = 0
    
    for i in range(4, len(df)):
        try:
            # Tower Bottom (Bullish)
            if (df.iloc[i]['close'] > df.iloc[i]['open'] and
                df.iloc[i]['close'] - df.iloc[i]['open'] > body and
                df.iloc[i-2]['low'] < df.iloc[i-1]['low'] and
                df.iloc[i-2]['low'] < df.iloc[i-3]['low'] and
                df.iloc[i-4]['close'] < df.iloc[i-4]['open'] and
                df.iloc[i-4]['open'] - df.iloc[i]['close'] > body):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'tower_bullish'] = 1
            
            # Tower Top (Bearish)
            elif (df.iloc[i]['close'] < df.iloc[i]['open'] and
                  df.iloc[i]['open'] - df.iloc[i]['close'] > body and
                  df.iloc[i-2]['high'] > df.iloc[i-1]['high'] and
                  df.iloc[i-2]['high'] > df.iloc[i-3]['high'] and
                  df.iloc[i-4]['close'] > df.iloc[i-4]['open'] and
                  df.iloc[i-4]['close'] - df.iloc[i]['open'] > body):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'tower_bearish'] = 1
        except (IndexError, KeyError):
            continue
    
    return df

def detect_on_neck(df):
    """
    Detect On Neck pattern.
    
    A two-candle pattern where the second candle closes exactly at the close of the first candle.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'on_neck_bullish' and 'on_neck_bearish' columns
    """
    df = df.copy()
    df = df.round(decimals=4)  # Round for exact price matching
    df['on_neck_bullish'] = 0
    df['on_neck_bearish'] = 0
    
    for i in range(1, len(df)):
        try:
            # Bullish On Neck
            if (df.iloc[i]['close'] > df.iloc[i]['open'] and
                df.iloc[i]['close'] == df.iloc[i-1]['close'] and
                df.iloc[i]['open'] < df.iloc[i-1]['close'] and
                df.iloc[i-1]['close'] < df.iloc[i-1]['open']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'on_neck_bullish'] = 1
            
            # Bearish On Neck
            elif (df.iloc[i]['close'] < df.iloc[i]['open'] and
                  df.iloc[i]['close'] == df.iloc[i-1]['close'] and
                  df.iloc[i]['open'] > df.iloc[i-1]['close'] and
                  df.iloc[i-1]['close'] > df.iloc[i-1]['open']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'on_neck_bearish'] = 1
        except (IndexError, KeyError):
            continue
    
    return df

# ============================================================================
# MODERN TREND-FOLLOWING PATTERNS
# ============================================================================

def detect_double_trouble(df, atr_period=14):
    """
    Detect Double Trouble pattern.
    
    A two-candle trend-following pattern that uses the Average True Range (ATR) for validation.
    Requires two consecutive same-color candles where the second candle's range exceeds 2x the ATR.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    atr_period : int
        ATR period (default: 14)
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'double_trouble_bullish' and 'double_trouble_bearish' columns
    """
    df = df.copy()
    df = calculate_atr(df, period=atr_period)
    df['double_trouble_bullish'] = 0
    df['double_trouble_bearish'] = 0
    
    for i in range(1, len(df)):
        try:
            if pd.isna(df.iloc[i-1]['atr']) or df.iloc[i-1]['atr'] == 0:
                continue
            
            # Bullish pattern
            if (df.iloc[i]['close'] > df.iloc[i]['open'] and
                df.iloc[i]['close'] > df.iloc[i-1]['close'] and
                df.iloc[i-1]['close'] > df.iloc[i-1]['open'] and
                df.iloc[i]['high'] - df.iloc[i]['low'] > (2 * df.iloc[i-1]['atr']) and
                df.iloc[i]['close'] - df.iloc[i]['open'] > df.iloc[i-1]['close'] - df.iloc[i-1]['open']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'double_trouble_bullish'] = 1
            
            # Bearish pattern
            elif (df.iloc[i]['close'] < df.iloc[i]['open'] and
                  df.iloc[i]['close'] < df.iloc[i-1]['close'] and
                  df.iloc[i-1]['close'] < df.iloc[i-1]['open'] and
                  df.iloc[i]['high'] - df.iloc[i]['low'] > (2 * df.iloc[i-1]['atr']) and
                  df.iloc[i]['open'] - df.iloc[i]['close'] > df.iloc[i-1]['open'] - df.iloc[i-1]['close']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'double_trouble_bearish'] = 1
        except (IndexError, KeyError):
            continue
    
    return df

def detect_bottle(df):
    """
    Detect Bottle pattern.
    
    A two-candle continuation pattern. Bullish: bullish candle → bullish candle with no low wick (open = low) that gaps below the previous close.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'bottle_bullish' and 'bottle_bearish' columns
    """
    df = df.copy()
    df['bottle_bullish'] = 0
    df['bottle_bearish'] = 0
    
    for i in range(1, len(df)):
        try:
            # Bullish Bottle: open == low, gaps below previous close
            if (df.iloc[i]['close'] > df.iloc[i]['open'] and
                df.iloc[i]['open'] == df.iloc[i]['low'] and
                df.iloc[i-1]['close'] > df.iloc[i-1]['open'] and
                df.iloc[i]['open'] < df.iloc[i-1]['close']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'bottle_bullish'] = 1
            
            # Bearish Bottle: open == high, gaps above previous close
            elif (df.iloc[i]['close'] < df.iloc[i]['open'] and
                  df.iloc[i]['open'] == df.iloc[i]['high'] and
                  df.iloc[i-1]['close'] < df.iloc[i-1]['open'] and
                  df.iloc[i]['open'] > df.iloc[i-1]['close']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'bottle_bearish'] = 1
        except (IndexError, KeyError):
            continue
    
    return df

def detect_slingshot(df):
    """
    Detect Slingshot pattern.
    
    A four-candle breakout/pullback continuation pattern. Bullish: two bullish candles establishing trend → two pullback candles → final candle breaks above.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'slingshot_bullish' and 'slingshot_bearish' columns
    """
    df = df.copy()
    df['slingshot_bullish'] = 0
    df['slingshot_bearish'] = 0
    
    for i in range(3, len(df)):
        try:
            # Bullish Slingshot
            if (df.iloc[i]['close'] > df.iloc[i-1]['high'] and
                df.iloc[i]['close'] > df.iloc[i-2]['high'] and
                df.iloc[i]['low'] <= df.iloc[i-3]['high'] and
                df.iloc[i]['close'] > df.iloc[i]['open'] and
                df.iloc[i-1]['close'] >= df.iloc[i-3]['high'] and
                df.iloc[i-2]['low'] >= df.iloc[i-3]['low'] and
                df.iloc[i-2]['close'] > df.iloc[i-2]['open'] and
                df.iloc[i-2]['close'] > df.iloc[i-3]['high'] and
                df.iloc[i-1]['high'] <= df.iloc[i-2]['high']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'slingshot_bullish'] = 1
            
            # Bearish Slingshot
            elif (df.iloc[i]['close'] < df.iloc[i-1]['low'] and
                  df.iloc[i]['close'] < df.iloc[i-2]['low'] and
                  df.iloc[i]['high'] >= df.iloc[i-3]['low'] and
                  df.iloc[i]['close'] < df.iloc[i]['open'] and
                  df.iloc[i-1]['high'] <= df.iloc[i-3]['high'] and
                  df.iloc[i-2]['close'] <= df.iloc[i-3]['low'] and
                  df.iloc[i-2]['close'] < df.iloc[i-2]['open'] and
                  df.iloc[i-2]['close'] < df.iloc[i-3]['low'] and
                  df.iloc[i-1]['low'] >= df.iloc[i-2]['low']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'slingshot_bearish'] = 1
        except (IndexError, KeyError):
            continue
    
    return df

def detect_h_pattern(df):
    """
    Detect H Pattern.
    
    A three-candle continuation pattern featuring a Doji (indecision candle) in the middle.
    Bullish: bullish candle → Doji (open = close) → bullish candle closing above the Doji with higher low.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'h_pattern_bullish' and 'h_pattern_bearish' columns
    """
    df = df.copy()
    df['h_pattern_bullish'] = 0
    df['h_pattern_bearish'] = 0
    
    for i in range(2, len(df)):
        try:
            # Bullish H pattern
            if (df.iloc[i]['close'] > df.iloc[i]['open'] and
                df.iloc[i]['close'] > df.iloc[i-1]['close'] and
                df.iloc[i]['low'] > df.iloc[i-1]['low'] and
                df.iloc[i-1]['close'] == df.iloc[i-1]['open'] and  # Doji
                df.iloc[i-2]['close'] > df.iloc[i-2]['open'] and
                df.iloc[i-2]['high'] < df.iloc[i-1]['high']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'h_pattern_bullish'] = 1
            
            # Bearish H pattern
            elif (df.iloc[i]['close'] < df.iloc[i]['open'] and
                  df.iloc[i]['close'] < df.iloc[i-1]['close'] and
                  df.iloc[i]['low'] < df.iloc[i-1]['low'] and
                  df.iloc[i-1]['close'] == df.iloc[i-1]['open'] and  # Doji
                  df.iloc[i-2]['close'] < df.iloc[i-2]['open'] and
                  df.iloc[i-2]['low'] > df.iloc[i-1]['low']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'h_pattern_bearish'] = 1
        except (IndexError, KeyError):
            continue
    
    return df

# ============================================================================
# MODERN CONTRARIAN PATTERNS
# ============================================================================

def detect_doppelganger(df):
    """
    Detect Doppelgänger pattern.
    
    A three-candle reversal pattern featuring two identical "twin" candles.
    Bullish: bearish candle → two candles with same highs and lows (the "twins").
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'doppelganger_bullish' and 'doppelganger_bearish' columns
    """
    df = df.copy()
    df = df.round(decimals=4)  # Round to 4 decimals for FX
    df['doppelganger_bullish'] = 0
    df['doppelganger_bearish'] = 0
    
    for i in range(2, len(df)):
        try:
            # Bullish Doppelgänger
            if (df.iloc[i-2]['close'] < df.iloc[i-2]['open'] and
                df.iloc[i-1]['close'] < df.iloc[i-2]['open'] and
                df.iloc[i]['high'] == df.iloc[i-1]['high'] and
                df.iloc[i]['low'] == df.iloc[i-1]['low']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'doppelganger_bullish'] = 1
            
            # Bearish Doppelgänger
            elif (df.iloc[i-2]['close'] > df.iloc[i-2]['open'] and
                  df.iloc[i-1]['close'] > df.iloc[i-2]['open'] and
                  df.iloc[i]['high'] == df.iloc[i-1]['high'] and
                  df.iloc[i]['low'] == df.iloc[i-1]['low']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'doppelganger_bearish'] = 1
        except (IndexError, KeyError):
            continue
    
    return df

def detect_blockade(df):
    """
    Detect Blockade pattern.
    
    A four-candle reversal pattern showing stabilization at support/resistance.
    Bullish: bearish candle → three candles with lows between the first candle's low and close → fourth bullish candle breaking above.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'blockade_bullish' and 'blockade_bearish' columns
    """
    df = df.copy()
    df['blockade_bullish'] = 0
    df['blockade_bearish'] = 0
    
    for i in range(3, len(df)):
        try:
            # Bullish Blockade
            if (df.iloc[i-3]['close'] < df.iloc[i-3]['open'] and
                df.iloc[i-2]['close'] < df.iloc[i-3]['open'] and
                df.iloc[i-2]['low'] >= df.iloc[i-3]['low'] and
                df.iloc[i-2]['low'] <= df.iloc[i-3]['close'] and
                df.iloc[i-1]['low'] >= df.iloc[i-3]['low'] and
                df.iloc[i-1]['low'] <= df.iloc[i-3]['close'] and
                df.iloc[i]['low'] >= df.iloc[i-3]['low'] and
                df.iloc[i]['low'] <= df.iloc[i-3]['close'] and
                df.iloc[i]['close'] > df.iloc[i]['open'] and
                df.iloc[i]['close'] > df.iloc[i-3]['high']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'blockade_bullish'] = 1
            
            # Bearish Blockade
            elif (df.iloc[i-3]['close'] > df.iloc[i-3]['open'] and
                  df.iloc[i-2]['close'] > df.iloc[i-3]['open'] and
                  df.iloc[i-2]['high'] <= df.iloc[i-3]['high'] and
                  df.iloc[i-2]['high'] >= df.iloc[i-3]['close'] and
                  df.iloc[i-1]['high'] <= df.iloc[i-3]['high'] and
                  df.iloc[i-1]['high'] >= df.iloc[i-3]['close'] and
                  df.iloc[i]['high'] <= df.iloc[i-3]['high'] and
                  df.iloc[i]['high'] >= df.iloc[i-3]['close'] and
                  df.iloc[i]['close'] < df.iloc[i]['open'] and
                  df.iloc[i]['close'] < df.iloc[i-3]['low']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'blockade_bearish'] = 1
        except (IndexError, KeyError):
            continue
    
    return df

def detect_barrier(df):
    """
    Detect Barrier pattern.
    
    A simplified three-candle version of the Blockade pattern.
    Bullish: two bearish candles → one bullish candle, all with the same low (support).
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'barrier_bullish' and 'barrier_bearish' columns
    """
    df = df.copy()
    df = df.round(decimals=4)  # Round for equal price matching
    df['barrier_bullish'] = 0
    df['barrier_bearish'] = 0
    
    for i in range(2, len(df)):
        try:
            # Bullish Barrier: same lows, last candle bullish
            if (df.iloc[i]['close'] > df.iloc[i]['open'] and
                df.iloc[i-1]['close'] < df.iloc[i-1]['open'] and
                df.iloc[i-2]['close'] < df.iloc[i-2]['open'] and
                df.iloc[i]['low'] == df.iloc[i-1]['low'] and
                df.iloc[i]['low'] == df.iloc[i-2]['low']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'barrier_bullish'] = 1
            
            # Bearish Barrier: same highs, last candle bearish
            elif (df.iloc[i]['close'] < df.iloc[i]['open'] and
                  df.iloc[i-1]['close'] > df.iloc[i-1]['open'] and
                  df.iloc[i-2]['close'] > df.iloc[i-2]['open'] and
                  df.iloc[i]['high'] == df.iloc[i-1]['high'] and
                  df.iloc[i]['high'] == df.iloc[i-2]['high']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'barrier_bearish'] = 1
        except (IndexError, KeyError):
            continue
    
    return df

def detect_mirror(df):
    """
    Detect Mirror pattern.
    
    A four-candle U-turn reversal pattern. Bullish: bearish candle → two candles with equal closes → bullish candle with high matching the first candle's high.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'mirror_bullish' and 'mirror_bearish' columns
    """
    df = df.copy()
    df = df.round(decimals=4)
    df['mirror_bullish'] = 0
    df['mirror_bearish'] = 0
    
    for i in range(3, len(df)):
        try:
            # Bullish Mirror
            if (df.iloc[i]['close'] > df.iloc[i]['open'] and
                df.iloc[i]['high'] == df.iloc[i-3]['high'] and
                df.iloc[i]['close'] > df.iloc[i-1]['close'] and
                df.iloc[i]['close'] > df.iloc[i-2]['close'] and
                df.iloc[i]['close'] > df.iloc[i-3]['close'] and
                df.iloc[i-3]['close'] < df.iloc[i-3]['open'] and
                df.iloc[i-1]['close'] == df.iloc[i-2]['close']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'mirror_bullish'] = 1
            
            # Bearish Mirror
            elif (df.iloc[i]['close'] < df.iloc[i]['open'] and
                  df.iloc[i]['low'] == df.iloc[i-3]['low'] and
                  df.iloc[i]['close'] < df.iloc[i-1]['close'] and
                  df.iloc[i]['close'] < df.iloc[i-2]['close'] and
                  df.iloc[i]['close'] < df.iloc[i-3]['close'] and
                  df.iloc[i-3]['close'] > df.iloc[i-3]['open'] and
                  df.iloc[i-1]['close'] == df.iloc[i-2]['close']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'mirror_bearish'] = 1
        except (IndexError, KeyError):
            continue
    
    return df

def detect_shrinking(df):
    """
    Detect Shrinking pattern.
    
    A five-candle breakout pattern after congestion. Bullish: bearish candle → three progressively smaller candles → bullish breakout candle.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'shrinking_bullish' and 'shrinking_bearish' columns
    """
    df = df.copy()
    df = df.round(decimals=4)
    df['shrinking_bullish'] = 0
    df['shrinking_bearish'] = 0
    
    for i in range(4, len(df)):
        try:
            # Bullish Shrinking
            if (df.iloc[i-4]['close'] < df.iloc[i-4]['open'] and
                df.iloc[i]['close'] > df.iloc[i]['open'] and
                df.iloc[i]['close'] > df.iloc[i-3]['high'] and
                abs(df.iloc[i-3]['close'] - df.iloc[i-3]['open']) <
                abs(df.iloc[i-4]['close'] - df.iloc[i-4]['open']) and
                abs(df.iloc[i-2]['close'] - df.iloc[i-2]['open']) <
                abs(df.iloc[i-3]['close'] - df.iloc[i-3]['open']) and
                abs(df.iloc[i-1]['close'] - df.iloc[i-1]['open']) <
                abs(df.iloc[i-2]['close'] - df.iloc[i-2]['open']) and
                df.iloc[i-1]['high'] < df.iloc[i-2]['high'] and
                df.iloc[i-2]['high'] < df.iloc[i-3]['high']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'shrinking_bullish'] = 1
            
            # Bearish Shrinking
            elif (df.iloc[i-4]['close'] > df.iloc[i-4]['open'] and
                  df.iloc[i]['close'] < df.iloc[i]['open'] and
                  df.iloc[i]['close'] < df.iloc[i-3]['low'] and
                  abs(df.iloc[i-3]['close'] - df.iloc[i-3]['open']) <
                  abs(df.iloc[i-4]['close'] - df.iloc[i-4]['open']) and
                  abs(df.iloc[i-2]['close'] - df.iloc[i-2]['open']) <
                  abs(df.iloc[i-3]['close'] - df.iloc[i-3]['open']) and
                  abs(df.iloc[i-1]['close'] - df.iloc[i-1]['open']) <
                  abs(df.iloc[i-2]['close'] - df.iloc[i-2]['open']) and
                  df.iloc[i-1]['low'] > df.iloc[i-2]['low'] and
                  df.iloc[i-2]['low'] > df.iloc[i-3]['low']):
                if i + 1 < len(df):
                    df.loc[df.index[i+1], 'shrinking_bearish'] = 1
        except (IndexError, KeyError):
            continue
    
    return df

