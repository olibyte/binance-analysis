import pandas as pd
# Calculate Bollinger Bands
def calculate_bollinger_bands(df, period=20, num_std=2):
    """
    Calculate Bollinger Bands for a DataFrame.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with price data (must have 'close' column)
    period : int
        Period for moving average (default: 20)
    num_std : float
        Number of standard deviations for bands (default: 2)
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added columns: 'bb_middle', 'bb_upper', 'bb_lower'
    """
    df = df.copy()
    df['bb_middle'] = df['close'].rolling(window=period).mean()
    std = df['close'].rolling(window=period).std()
    df['bb_upper'] = df['bb_middle'] + (std * num_std)
    df['bb_lower'] = df['bb_middle'] - (std * num_std)
    return df

# Calculate K's Envelopes
def calculate_k_envelopes(df, lookback=800):
    """
    Calculate K's Envelopes - moving averages on highs and lows.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    lookback : int
        Period for moving averages (default: 800)
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'k_envelope_upper' and 'k_envelope_lower' columns
    """
    df = df.copy()
    df['k_envelope_upper'] = df['high'].rolling(window=lookback).mean()
    df['k_envelope_lower'] = df['low'].rolling(window=lookback).mean()
    return df

# Volume Confirmation Functions
def calculate_volume_indicators(df, fast_period=20, slow_period=50):
    """
    Calculate volume moving averages and volume spike detection.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with volume data
    fast_period : int
        Fast moving average period (default: 20)
    slow_period : int
        Slow moving average period (default: 50)
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added volume indicator columns
    """
    df = df.copy()
    
    # Volume moving averages
    df['vol_ma_fast'] = df['volume'].rolling(window=fast_period).mean()
    df['vol_ma_slow'] = df['volume'].rolling(window=slow_period).mean()
    
    # Volume spike detection (volume > 1.5x of fast MA)
    df['volume_spike'] = df['volume'] > (df['vol_ma_fast'] * 1.5)
    
    # Volume trend (comparing recent volume to average)
    df['volume_trend'] = df['volume'].rolling(window=5).mean() / df['vol_ma_fast']
    
    return df

def check_volume_confirmation(df, pattern_idx, pattern_type, lookback=5):
    """
    Check if volume confirms the euphoria pattern.
    
    For BUY signals (bullish euphoria - three red candles):
    - Volume should be decreasing during pattern formation (exhaustion)
    - Volume spike on signal candle is a bonus
    
    For SELL signals (bearish euphoria - three green candles):
    - Volume should be decreasing during pattern formation (exhaustion)
    - Volume spike on signal candle is a bonus
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with volume and euphoria data
    pattern_idx : int
        Index where euphoria pattern was detected
    pattern_type : str
        'bullish' or 'bearish'
    lookback : int
        Number of candles to check before pattern (default: 5)
    
    Returns:
    --------
    dict
        Dictionary with confirmation status and details
    """
    if pattern_idx < lookback:
        return {'confirmed': False, 'reason': 'Insufficient data'}
    
    # Get pattern candles (last 3 candles form the pattern)
    pattern_start = pattern_idx - 2
    signal_candle = pattern_idx + 1  # Signal is on next candle
    
    if signal_candle >= len(df):
        return {'confirmed': False, 'reason': 'No signal candle'}
    
    # Check volume during pattern formation (candles -2, -1, 0)
    pattern_volumes = df.iloc[pattern_start:pattern_idx+1]['volume'].values
    pre_pattern_volumes = df.iloc[pattern_start-lookback:pattern_start]['volume'].values
    
    # Volume trend: decreasing volume suggests exhaustion
    pattern_avg_vol = pattern_volumes.mean()
    pre_pattern_avg_vol = pre_pattern_volumes.mean() if len(pre_pattern_volumes) > 0 else pattern_avg_vol
    
    # Volume decreasing during pattern (exhaustion signal)
    volume_decreasing = pattern_avg_vol < pre_pattern_avg_vol
    
    # Check for volume spike on signal candle
    signal_volume = df.iloc[signal_candle]['volume']
    signal_vol_ma = df.iloc[signal_candle]['vol_ma_fast']
    volume_spike = signal_volume > (signal_vol_ma * 1.5) if not pd.isna(signal_vol_ma) else False
    
    # Confirmation criteria:
    # 1. Volume decreasing during pattern (exhaustion) - required
    # 2. Volume spike on signal candle - bonus (increases conviction)
    confirmed = volume_decreasing
    
    return {
        'confirmed': confirmed,
        'volume_decreasing': volume_decreasing,
        'volume_spike': volume_spike,
        'pattern_avg_volume': pattern_avg_vol,
        'pre_pattern_avg_volume': pre_pattern_avg_vol,
        'signal_volume': signal_volume,
        'signal_vol_ma': signal_vol_ma,
        'conviction': 'high' if (volume_decreasing and volume_spike) else 'medium' if volume_decreasing else 'low'
    }

def check_volume_participation(df, signal_idx, signal_type, vol_fast_period=20, vol_slow_period=50, spike_threshold=1.5, lookback=5):
    """
    Check if volume participates in RSI trading signals.
    
    For RSI signals, volume participation means:
    - Volume spike (volume > threshold * fast MA) - primary confirmation
    - Volume above average (volume > fast MA) - secondary confirmation
    - Volume trend increasing (recent volume > previous average) - tertiary confirmation
    
    This is different from euphoria patterns where decreasing volume indicates exhaustion.
    For RSI signals, we want increasing volume/spike to confirm the move.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with volume and RSI data (must have volume indicators calculated)
    signal_idx : int
        Index where RSI signal was detected (the signal candle)
    signal_type : str
        'buy' or 'sell' - type of signal
    vol_fast_period : int
        Fast volume MA period (default: 20)
    vol_slow_period : int
        Slow volume MA period (default: 50)
    spike_threshold : float
        Multiplier for volume spike detection (default: 1.5)
    lookback : int
        Number of candles to check for volume trend (default: 5)
    
    Returns:
    --------
    dict
        Dictionary with volume participation status and details
    """
    if signal_idx >= len(df):
        return {'confirmed': False, 'reason': 'Invalid index'}
    
    # Check if volume indicators exist, calculate if not
    if 'vol_ma_fast' not in df.columns:
        df = calculate_volume_indicators(df, fast_period=vol_fast_period, slow_period=vol_slow_period)
    
    signal_candle = df.iloc[signal_idx]
    signal_volume = signal_candle['volume']
    signal_vol_ma_fast = signal_candle.get('vol_ma_fast', None)
    
    if pd.isna(signal_vol_ma_fast) or signal_vol_ma_fast is None or signal_vol_ma_fast == 0:
        return {'confirmed': False, 'reason': 'Insufficient volume data'}
    
    # Check for volume spike (primary confirmation)
    volume_spike = signal_volume > (signal_vol_ma_fast * spike_threshold)
    
    # Check if volume is above average (secondary confirmation)
    volume_above_avg = signal_volume > signal_vol_ma_fast
    
    # Check volume trend (increasing volume over recent period)
    volume_trend_increasing = False
    if signal_idx >= lookback:
        recent_volumes = df.iloc[signal_idx - lookback:signal_idx]['volume'].values
        if len(recent_volumes) > 0:
            recent_avg = recent_volumes.mean()
            volume_trend_increasing = signal_volume > recent_avg
    
    # Determine confirmation and conviction
    # Primary: volume spike = high conviction
    # Secondary: volume above avg + increasing trend = medium conviction
    # Tertiary: volume above avg only = low conviction
    # No participation: volume below avg = not confirmed
    
    confirmed = False
    conviction = 'low'
    reason = ''
    
    if volume_spike:
        confirmed = True
        conviction = 'high'
        reason = 'Volume Spike'
    elif volume_above_avg and volume_trend_increasing:
        confirmed = True
        conviction = 'medium'
        reason = 'Volume Above Avg + Increasing'
    elif volume_above_avg:
        confirmed = True
        conviction = 'low'
        reason = 'Volume Above Avg'
    else:
        reason = 'Volume Below Avg'
    
    return {
        'confirmed': confirmed,
        'volume_spike': volume_spike,
        'volume_above_avg': volume_above_avg,
        'volume_trend_increasing': volume_trend_increasing,
        'signal_volume': signal_volume,
        'signal_vol_ma_fast': signal_vol_ma_fast,
        'conviction': conviction,
        'reason': reason
    }

# RSI Calculation and Analysis Functions
def calculate_rsi(df, period=14):
    """
    Calculate Relative Strength Index (RSI).
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with price data (must have 'close' column)
    period : int
        RSI period (default: 14)
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'rsi' column
    """
    df = df.copy()
    delta = df['close'].diff()
    
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    return df

def detect_rsi_divergence(df, lookback=20, min_swings=2):
    """
    Detect RSI divergences (bearish and bullish).
    
    Bearish Divergence: Price makes higher highs, RSI makes lower highs
    Bullish Divergence: Price makes lower lows, RSI makes higher lows
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with price and RSI data
    lookback : int
        Number of periods to look back for swing points
    min_swings : int
        Minimum number of swing points to confirm divergence
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added divergence columns
    """
    df = df.copy()
    df['bearish_divergence'] = False
    df['bullish_divergence'] = False
    df['rsi_overbought'] = df['rsi'] > 70
    df['rsi_oversold'] = df['rsi'] < 30
    
    # Find swing highs and lows
    for i in range(lookback, len(df) - lookback):
        # Check for bearish divergence (price higher highs, RSI lower highs)
        price_window = df.iloc[i-lookback:i+lookback+1]
        rsi_window = df.iloc[i-lookback:i+lookback+1]
        
        # Find local highs in price
        price_highs = price_window[price_window['high'] == price_window['high'].rolling(window=5, center=True).max()]
        rsi_highs = rsi_window.loc[price_highs.index, 'rsi'] if len(price_highs) > 0 else pd.Series()
        
        if len(price_highs) >= 2 and len(rsi_highs) >= 2:
            # Check if price is making higher highs
            price_highs_sorted = price_highs.sort_index()
            if len(price_highs_sorted) >= 2:
                recent_high = price_highs_sorted.iloc[-1]['high']
                prev_high = price_highs_sorted.iloc[-2]['high']
                
                # Check if RSI is making lower highs
                recent_rsi = rsi_highs.iloc[-1]
                prev_rsi = rsi_highs.iloc[-2] if len(rsi_highs) >= 2 else recent_rsi
                
                if recent_high > prev_high and recent_rsi < prev_rsi and not pd.isna(recent_rsi) and not pd.isna(prev_rsi):
                    df.loc[price_highs_sorted.index[-1], 'bearish_divergence'] = True
        
        # Find local lows in price
        price_lows = price_window[price_window['low'] == price_window['low'].rolling(window=5, center=True).min()]
        rsi_lows = rsi_window.loc[price_lows.index, 'rsi'] if len(price_lows) > 0 else pd.Series()
        
        if len(price_lows) >= 2 and len(rsi_lows) >= 2:
            # Check if price is making lower lows
            price_lows_sorted = price_lows.sort_index()
            if len(price_lows_sorted) >= 2:
                recent_low = price_lows_sorted.iloc[-1]['low']
                prev_low = price_lows_sorted.iloc[-2]['low']
                
                # Check if RSI is making higher lows
                recent_rsi = rsi_lows.iloc[-1]
                prev_rsi = rsi_lows.iloc[-2] if len(rsi_lows) >= 2 else recent_rsi
                
                if recent_low < prev_low and recent_rsi > prev_rsi and not pd.isna(recent_rsi) and not pd.isna(prev_rsi):
                    df.loc[price_lows_sorted.index[-1], 'bullish_divergence'] = True
    
    return df

def check_rsi_confirmation(df, pattern_idx, pattern_type):
    """
    Check if RSI confirms the euphoria pattern.
    
    For BUY signals (bullish euphoria - three red candles):
    - RSI should be oversold (<30) OR showing bullish divergence
    - Overbought RSI (>70) would contradict the buy signal
    
    For SELL signals (bearish euphoria - three green candles):
    - RSI should be overbought (>70) OR showing bearish divergence
    - Oversold RSI (<30) would contradict the sell signal
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with RSI and euphoria data
    pattern_idx : int
        Index where euphoria pattern was detected
    pattern_type : str
        'bullish' or 'bearish'
    
    Returns:
    --------
    dict
        Dictionary with RSI confirmation status and details
    """
    if pattern_idx >= len(df):
        return {'confirmed': False, 'reason': 'Invalid index'}
    
    curr = df.iloc[pattern_idx]
    signal_candle = pattern_idx + 1
    
    if signal_candle >= len(df):
        return {'confirmed': False, 'reason': 'No signal candle'}
    
    signal_rsi = df.iloc[signal_candle]['rsi']
    
    if pd.isna(signal_rsi):
        return {'confirmed': False, 'reason': 'No RSI data'}
    
    confirmed = False
    reason = ''
    conviction = 'low'
    
    if pattern_type == 'bullish':  # BUY signal
        # For buy signals, we want oversold RSI or bullish divergence
        if signal_rsi < 30:
            confirmed = True
            reason = 'RSI Oversold'
            conviction = 'high'
        elif df.iloc[signal_candle]['bullish_divergence']:
            confirmed = True
            reason = 'Bullish Divergence'
            conviction = 'high'
        elif signal_rsi < 50:  # RSI below midpoint (weakening but not oversold)
            confirmed = True
            reason = 'RSI Below Midpoint'
            conviction = 'medium'
        else:
            reason = f'RSI Too High ({signal_rsi:.1f})'
    
    elif pattern_type == 'bearish':  # SELL signal
        # For sell signals, we want overbought RSI or bearish divergence
        if signal_rsi > 70:
            confirmed = True
            reason = 'RSI Overbought'
            conviction = 'high'
        elif df.iloc[signal_candle]['bearish_divergence']:
            confirmed = True
            reason = 'Bearish Divergence'
            conviction = 'high'
        elif signal_rsi > 50:  # RSI above midpoint (strengthening but not overbought)
            confirmed = True
            reason = 'RSI Above Midpoint'
            conviction = 'medium'
        else:
            reason = f'RSI Too Low ({signal_rsi:.1f})'
    
    return {
        'confirmed': confirmed,
        'rsi': signal_rsi,
        'reason': reason,
        'conviction': conviction,
        'overbought': signal_rsi > 70,
        'oversold': signal_rsi < 30,
        'bearish_divergence': df.iloc[signal_candle]['bearish_divergence'] if signal_candle < len(df) else False,
        'bullish_divergence': df.iloc[signal_candle]['bullish_divergence'] if signal_candle < len(df) else False
    }

# MACD Calculation and Analysis Functions
def calculate_macd(df, fast_period=12, slow_period=26, signal_period=9):
    """
    Calculate Moving Average Convergence Divergence (MACD).
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with price data (must have 'close' column)
    fast_period : int
        Fast EMA period (default: 12)
    slow_period : int
        Slow EMA period (default: 26)
    signal_period : int
        Signal line EMA period (default: 9)
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added columns: 'macd', 'macd_signal', 'macd_histogram'
    """
    df = df.copy()
    
    # Calculate EMAs
    ema_fast = df['close'].ewm(span=fast_period, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow_period, adjust=False).mean()
    
    # MACD line = Fast EMA - Slow EMA
    df['macd'] = ema_fast - ema_slow
    
    # Signal line = EMA of MACD line
    df['macd_signal'] = df['macd'].ewm(span=signal_period, adjust=False).mean()
    
    # Histogram = MACD line - Signal line
    df['macd_histogram'] = df['macd'] - df['macd_signal']
    
    return df

def detect_macd_divergence(df, lookback=20):
    """
    Detect MACD divergences (bearish and bullish).
    
    Bearish Divergence: Price makes higher highs, MACD makes lower highs
    Bullish Divergence: Price makes lower lows, MACD makes higher lows
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with price and MACD data
    lookback : int
        Number of periods to look back for swing points
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added divergence columns
    """
    df = df.copy()
    df['macd_bearish_divergence'] = False
    df['macd_bullish_divergence'] = False
    
    # Find swing highs and lows
    for i in range(lookback, len(df) - lookback):
        # Check for bearish divergence (price higher highs, MACD lower highs)
        price_window = df.iloc[i-lookback:i+lookback+1]
        macd_window = df.iloc[i-lookback:i+lookback+1]
        
        # Find local highs in price
        price_highs = price_window[price_window['high'] == price_window['high'].rolling(window=5, center=True).max()]
        macd_highs = macd_window.loc[price_highs.index, 'macd'] if len(price_highs) > 0 else pd.Series()
        
        if len(price_highs) >= 2 and len(macd_highs) >= 2:
            # Check if price is making higher highs
            price_highs_sorted = price_highs.sort_index()
            if len(price_highs_sorted) >= 2:
                recent_high = price_highs_sorted.iloc[-1]['high']
                prev_high = price_highs_sorted.iloc[-2]['high']
                
                # Check if MACD is making lower highs
                recent_macd = macd_highs.iloc[-1]
                prev_macd = macd_highs.iloc[-2] if len(macd_highs) >= 2 else recent_macd
                
                if recent_high > prev_high and recent_macd < prev_macd and not pd.isna(recent_macd) and not pd.isna(prev_macd):
                    df.loc[price_highs_sorted.index[-1], 'macd_bearish_divergence'] = True
        
        # Find local lows in price
        price_lows = price_window[price_window['low'] == price_window['low'].rolling(window=5, center=True).min()]
        macd_lows = macd_window.loc[price_lows.index, 'macd'] if len(price_lows) > 0 else pd.Series()
        
        if len(price_lows) >= 2 and len(macd_lows) >= 2:
            # Check if price is making lower lows
            price_lows_sorted = price_lows.sort_index()
            if len(price_lows_sorted) >= 2:
                recent_low = price_lows_sorted.iloc[-1]['low']
                prev_low = price_lows_sorted.iloc[-2]['low']
                
                # Check if MACD is making higher lows
                recent_macd = macd_lows.iloc[-1]
                prev_macd = macd_lows.iloc[-2] if len(macd_lows) >= 2 else recent_macd
                
                if recent_low < prev_low and recent_macd > prev_macd and not pd.isna(recent_macd) and not pd.isna(prev_macd):
                    df.loc[price_lows_sorted.index[-1], 'macd_bullish_divergence'] = True
    
    return df

def check_macd_confirmation(df, pattern_idx, pattern_type, lookback_candles=5):
    """
    Check if MACD confirms the euphoria pattern.
    
    For BUY signals (bullish euphoria - three red candles):
    - Bearish MACD crossover (MACD crosses below signal) OR
    - Bullish MACD divergence OR
    - Histogram shrinking (momentum decelerating)
    
    For SELL signals (bearish euphoria - three green candles):
    - Bearish MACD crossover (MACD crosses below signal) OR
    - Bearish MACD divergence OR
    - Histogram shrinking (momentum decelerating)
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with MACD and euphoria data
    pattern_idx : int
        Index where euphoria pattern was detected
    pattern_type : str
        'bullish' or 'bearish'
    lookback_candles : int
        Number of candles to check for crossover after pattern (default: 5)
    
    Returns:
    --------
    dict
        Dictionary with MACD confirmation status and details
    """
    if pattern_idx >= len(df):
        return {'confirmed': False, 'reason': 'Invalid index'}
    
    signal_candle = pattern_idx + 1
    
    if signal_candle >= len(df):
        return {'confirmed': False, 'reason': 'No signal candle'}
    
    # Check if MACD data exists
    if pd.isna(df.iloc[signal_candle]['macd']) or pd.isna(df.iloc[signal_candle]['macd_signal']):
        return {'confirmed': False, 'reason': 'No MACD data'}
    
    confirmed = False
    reason = ''
    conviction = 'low'
    
    # Get MACD values at signal candle and previous candles
    signal_macd = df.iloc[signal_candle]['macd']
    signal_macd_signal = df.iloc[signal_candle]['macd_signal']
    signal_histogram = df.iloc[signal_candle]['macd_histogram']
    
    # Check for bearish crossover (MACD crosses below signal line)
    bearish_crossover = False
    if signal_candle > 0:
        prev_macd = df.iloc[signal_candle - 1]['macd']
        prev_macd_signal = df.iloc[signal_candle - 1]['macd_signal']
        # Crossover: previous MACD was above signal, now MACD is below signal
        if prev_macd > prev_macd_signal and signal_macd < signal_macd_signal:
            bearish_crossover = True
    
    # Check for bullish crossover (MACD crosses above signal line)
    bullish_crossover = False
    if signal_candle > 0:
        prev_macd = df.iloc[signal_candle - 1]['macd']
        prev_macd_signal = df.iloc[signal_candle - 1]['macd_signal']
        # Crossover: previous MACD was below signal, now MACD is above signal
        if prev_macd < prev_macd_signal and signal_macd > signal_macd_signal:
            bullish_crossover = True
    
    # Check for divergence
    macd_bearish_div = df.iloc[signal_candle]['macd_bearish_divergence'] if signal_candle < len(df) else False
    macd_bullish_div = df.iloc[signal_candle]['macd_bullish_divergence'] if signal_candle < len(df) else False
    
    # Check histogram shrinking (momentum deceleration)
    histogram_shrinking = False
    if signal_candle >= lookback_candles:
        # Compare current histogram to average of previous candles
        recent_histograms = df.iloc[signal_candle - lookback_candles:signal_candle]['macd_histogram']
        if len(recent_histograms) > 0 and not recent_histograms.isna().all():
            avg_histogram = recent_histograms.abs().mean()
            if abs(signal_histogram) < avg_histogram * 0.7:  # Histogram shrunk by 30%+
                histogram_shrinking = True
    
    if pattern_type == 'bullish':  # BUY signal
        # For buy signals, we want bearish MACD crossover OR bullish divergence OR histogram shrinking
        if bearish_crossover:
            confirmed = True
            reason = 'Bearish Crossover'
            conviction = 'high'
        elif macd_bullish_div:
            confirmed = True
            reason = 'Bullish Divergence'
            conviction = 'high'
        elif histogram_shrinking:
            confirmed = True
            reason = 'Histogram Shrinking'
            conviction = 'medium'
        else:
            reason = 'No MACD Confirmation'
    
    elif pattern_type == 'bearish':  # SELL signal
        # For sell signals, we want bearish MACD crossover OR bearish divergence OR histogram shrinking
        if bearish_crossover:
            confirmed = True
            reason = 'Bearish Crossover'
            conviction = 'high'
        elif macd_bearish_div:
            confirmed = True
            reason = 'Bearish Divergence'
            conviction = 'high'
        elif histogram_shrinking:
            confirmed = True
            reason = 'Histogram Shrinking'
            conviction = 'medium'
        else:
            reason = 'No MACD Confirmation'
    
    return {
        'confirmed': confirmed,
        'macd': signal_macd,
        'macd_signal': signal_macd_signal,
        'macd_histogram': signal_histogram,
        'reason': reason,
        'conviction': conviction,
        'bearish_crossover': bearish_crossover,
        'bullish_crossover': bullish_crossover,
        'bearish_divergence': macd_bearish_div,
        'bullish_divergence': macd_bullish_div,
        'histogram_shrinking': histogram_shrinking
    }

# ADX Calculation and Analysis Functions
def calculate_adx(df, period=14):
    """
    Calculate Average Directional Index (ADX) with +DI and -DI.
    
    ADX measures trend strength regardless of direction.
    +DI (Plus Directional Indicator) measures upward price movement.
    -DI (Minus Directional Indicator) measures downward price movement.
    
    Uses Wilder's smoothing method for calculations.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data (must have 'high', 'low', 'close' columns)
    period : int
        ADX period (default: 14)
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added columns: 'adx', 'adx_plus_di', 'adx_minus_di'
    """
    df = df.copy()
    
    # Calculate True Range (TR)
    df['tr1'] = df['high'] - df['low']
    df['tr2'] = abs(df['high'] - df['close'].shift(1))
    df['tr3'] = abs(df['low'] - df['close'].shift(1))
    df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
    
    # Calculate Directional Movement
    df['plus_dm'] = 0.0
    df['minus_dm'] = 0.0
    
    # +DM: current high - previous high (if positive and > |current low - previous low|)
    # -DM: previous low - current low (if positive and > |current high - previous high|)
    for i in range(1, len(df)):
        up_move = df.iloc[i]['high'] - df.iloc[i-1]['high']
        down_move = df.iloc[i-1]['low'] - df.iloc[i]['low']
        
        if up_move > down_move and up_move > 0:
            df.iloc[i, df.columns.get_loc('plus_dm')] = up_move
        elif down_move > up_move and down_move > 0:
            df.iloc[i, df.columns.get_loc('minus_dm')] = down_move
    
    # Smooth TR, +DM, and -DM using Wilder's smoothing
    # First value is simple sum, then use Wilder's method: smoothed = previous - (previous / period) + current
    df['tr_smooth'] = df['tr'].copy()
    df['plus_dm_smooth'] = df['plus_dm'].copy()
    df['minus_dm_smooth'] = df['minus_dm'].copy()
    
    # Calculate initial sum for first period values
    for i in range(period, len(df)):
        if i == period:
            # First smoothed value is sum of first period values
            df.iloc[i, df.columns.get_loc('tr_smooth')] = df.iloc[i-period+1:i+1]['tr'].sum()
            df.iloc[i, df.columns.get_loc('plus_dm_smooth')] = df.iloc[i-period+1:i+1]['plus_dm'].sum()
            df.iloc[i, df.columns.get_loc('minus_dm_smooth')] = df.iloc[i-period+1:i+1]['minus_dm'].sum()
        else:
            # Wilder's smoothing: smoothed = previous - (previous / period) + current
            prev_tr = df.iloc[i-1]['tr_smooth']
            prev_plus_dm = df.iloc[i-1]['plus_dm_smooth']
            prev_minus_dm = df.iloc[i-1]['minus_dm_smooth']
            
            df.iloc[i, df.columns.get_loc('tr_smooth')] = prev_tr - (prev_tr / period) + df.iloc[i]['tr']
            df.iloc[i, df.columns.get_loc('plus_dm_smooth')] = prev_plus_dm - (prev_plus_dm / period) + df.iloc[i]['plus_dm']
            df.iloc[i, df.columns.get_loc('minus_dm_smooth')] = prev_minus_dm - (prev_minus_dm / period) + df.iloc[i]['minus_dm']
    
    # Calculate +DI and -DI as percentages
    df['adx_plus_di'] = 100 * (df['plus_dm_smooth'] / df['tr_smooth'])
    df['adx_minus_di'] = 100 * (df['minus_dm_smooth'] / df['tr_smooth'])
    
    # Calculate DX (Directional Index)
    df['dx'] = 100 * abs(df['adx_plus_di'] - df['adx_minus_di']) / (df['adx_plus_di'] + df['adx_minus_di'])
    
    # Calculate ADX as smoothed average of DX using Wilder's smoothing
    df['adx'] = df['dx'].copy()
    
    for i in range(period * 2 - 1, len(df)):
        if i == period * 2 - 1:
            # First ADX value is average of first period DX values
            df.iloc[i, df.columns.get_loc('adx')] = df.iloc[i-period+1:i+1]['dx'].mean()
        else:
            # Wilder's smoothing for ADX
            prev_adx = df.iloc[i-1]['adx']
            df.iloc[i, df.columns.get_loc('adx')] = prev_adx - (prev_adx / period) + df.iloc[i]['dx']
    
    # Clean up temporary columns
    df = df.drop(columns=['tr1', 'tr2', 'tr3', 'tr', 'plus_dm', 'minus_dm', 
                          'tr_smooth', 'plus_dm_smooth', 'minus_dm_smooth', 'dx'])
    
    return df

def check_adx_confirmation(df, pattern_idx, pattern_type):
    """
    Check if ADX confirms the euphoria pattern.
    
    ADX measures trend strength, while +DI and -DI indicate direction.
    For confirmation, we need both:
    - ADX > 20 (trend strength threshold)
    - Correct directional alignment (+DI > -DI for bullish, +DI < -DI for bearish)
    
    For BUY signals (bullish euphoria - three red candles):
    - ADX > 20 AND +DI > -DI (bullish trend direction)
    
    For SELL signals (bearish euphoria - three green candles):
    - ADX > 20 AND +DI < -DI (bearish trend direction)
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with ADX and euphoria data
    pattern_idx : int
        Index where euphoria pattern was detected
    pattern_type : str
        'bullish' or 'bearish'
    
    Returns:
    --------
    dict
        Dictionary with ADX confirmation status and details
    """
    if pattern_idx >= len(df):
        return {'confirmed': False, 'reason': 'Invalid index'}
    
    signal_candle = pattern_idx + 1
    
    if signal_candle >= len(df):
        return {'confirmed': False, 'reason': 'No signal candle'}
    
    # Check if ADX data exists
    if pd.isna(df.iloc[signal_candle]['adx']) or pd.isna(df.iloc[signal_candle]['adx_plus_di']) or pd.isna(df.iloc[signal_candle]['adx_minus_di']):
        return {'confirmed': False, 'reason': 'No ADX data'}
    
    signal_adx = df.iloc[signal_candle]['adx']
    signal_plus_di = df.iloc[signal_candle]['adx_plus_di']
    signal_minus_di = df.iloc[signal_candle]['adx_minus_di']
    
    confirmed = False
    reason = ''
    conviction = 'low'
    
    # Check ADX strength threshold
    adx_strong = signal_adx > 20
    adx_very_strong = signal_adx > 25
    
    if pattern_type == 'bullish':  # BUY signal
        # For buy signals, we want ADX > 20 AND +DI > -DI (bullish trend)
        di_bullish = signal_plus_di > signal_minus_di
        
        if adx_strong and di_bullish:
            confirmed = True
            if adx_very_strong:
                reason = 'ADX Very Strong + Bullish DI'
                conviction = 'high'
            else:
                reason = 'ADX Strong + Bullish DI'
                conviction = 'medium'
        elif adx_strong:
            reason = f'ADX Strong but Bearish DI ({signal_plus_di:.1f} < {signal_minus_di:.1f})'
        elif di_bullish:
            reason = f'Bullish DI but Weak ADX ({signal_adx:.1f} <= 20)'
        else:
            reason = f'Weak ADX ({signal_adx:.1f}) and Bearish DI'
    
    elif pattern_type == 'bearish':  # SELL signal
        # For sell signals, we want ADX > 20 AND +DI < -DI (bearish trend)
        di_bearish = signal_plus_di < signal_minus_di
        
        if adx_strong and di_bearish:
            confirmed = True
            if adx_very_strong:
                reason = 'ADX Very Strong + Bearish DI'
                conviction = 'high'
            else:
                reason = 'ADX Strong + Bearish DI'
                conviction = 'medium'
        elif adx_strong:
            reason = f'ADX Strong but Bullish DI ({signal_plus_di:.1f} > {signal_minus_di:.1f})'
        elif di_bearish:
            reason = f'Bearish DI but Weak ADX ({signal_adx:.1f} <= 20)'
        else:
            reason = f'Weak ADX ({signal_adx:.1f}) and Bullish DI'
    
    return {
        'confirmed': confirmed,
        'adx': signal_adx,
        'adx_plus_di': signal_plus_di,
        'adx_minus_di': signal_minus_di,
        'reason': reason,
        'conviction': conviction,
        'adx_strong': adx_strong,
        'adx_very_strong': adx_very_strong
    }

# ============================================================================
# LUXALGO SUPPORT AND RESISTANCE LEVELS
# ============================================================================
# This work is licensed under a Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)
# https://creativecommons.org/licenses/by-nc-sa/4.0/
# © LuxAlgo

def detect_pivot_high(df, left_bars=15, right_bars=15):
    """
    Detect pivot high points in price data.
    
    A pivot high is identified when the high at index i is the highest value
    in the window [i-left_bars : i+right_bars+1].
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data (must have 'high' column)
    left_bars : int
        Number of bars to look back (default: 15)
    right_bars : int
        Number of bars to look forward (default: 15)
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'pivot_high' column containing pivot high prices
        (NaN where no pivot is detected)
    """
    df = df.copy()
    df['pivot_high'] = float('nan')
    
    # Need at least left_bars + right_bars + 1 candles to detect pivots
    min_required = left_bars + right_bars + 1
    
    if len(df) < min_required:
        return df
    
    # For each potential pivot point
    for i in range(left_bars, len(df) - right_bars):
        # Get the window around this point
        window_start = i - left_bars
        window_end = i + right_bars + 1
        window_highs = df.iloc[window_start:window_end]['high']
        
        # Check if current high is the maximum in the window
        if df.iloc[i]['high'] == window_highs.max():
            # Additional check: ensure it's strictly greater than adjacent values
            # (to avoid flat tops being detected multiple times)
            if i > 0 and i < len(df) - 1:
                if (df.iloc[i]['high'] > df.iloc[i-1]['high'] and 
                    df.iloc[i]['high'] > df.iloc[i+1]['high']):
                    df.loc[df.index[i], 'pivot_high'] = df.iloc[i]['high']
            else:
                df.loc[df.index[i], 'pivot_high'] = df.iloc[i]['high']
    
    return df

def detect_pivot_low(df, left_bars=15, right_bars=15):
    """
    Detect pivot low points in price data.
    
    A pivot low is identified when the low at index i is the lowest value
    in the window [i-left_bars : i+right_bars+1].
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data (must have 'low' column)
    left_bars : int
        Number of bars to look back (default: 15)
    right_bars : int
        Number of bars to look forward (default: 15)
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'pivot_low' column containing pivot low prices
        (NaN where no pivot is detected)
    """
    df = df.copy()
    df['pivot_low'] = float('nan')
    
    # Need at least left_bars + right_bars + 1 candles to detect pivots
    min_required = left_bars + right_bars + 1
    
    if len(df) < min_required:
        return df
    
    # For each potential pivot point
    for i in range(left_bars, len(df) - right_bars):
        # Get the window around this point
        window_start = i - left_bars
        window_end = i + right_bars + 1
        window_lows = df.iloc[window_start:window_end]['low']
        
        # Check if current low is the minimum in the window
        if df.iloc[i]['low'] == window_lows.min():
            # Additional check: ensure it's strictly less than adjacent values
            # (to avoid flat bottoms being detected multiple times)
            if i > 0 and i < len(df) - 1:
                if (df.iloc[i]['low'] < df.iloc[i-1]['low'] and 
                    df.iloc[i]['low'] < df.iloc[i+1]['low']):
                    df.loc[df.index[i], 'pivot_low'] = df.iloc[i]['low']
            else:
                df.loc[df.index[i], 'pivot_low'] = df.iloc[i]['low']
    
    return df

def calculate_volume_oscillator(df, fast_period=5, slow_period=10):
    """
    Calculate volume oscillator using EMA-based volume analysis.
    
    Volume Oscillator = 100 * (EMA(volume, fast) - EMA(volume, slow)) / EMA(volume, slow)
    
    This measures the percentage difference between fast and slow volume EMAs,
    indicating volume momentum and participation.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with volume data (must have 'volume' column)
    fast_period : int
        Fast EMA period (default: 5)
    slow_period : int
        Slow EMA period (default: 10)
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added 'volume_osc' column
    """
    df = df.copy()
    
    # Calculate EMAs for volume
    df['vol_ema_fast'] = df['volume'].ewm(span=fast_period, adjust=False).mean()
    df['vol_ema_slow'] = df['volume'].ewm(span=slow_period, adjust=False).mean()
    
    # Calculate volume oscillator
    # Avoid division by zero
    df['volume_osc'] = 100 * (df['vol_ema_fast'] - df['vol_ema_slow']) / df['vol_ema_slow'].replace(0, float('nan'))
    
    # Clean up temporary columns
    df = df.drop(columns=['vol_ema_fast', 'vol_ema_slow'])
    
    return df

def calculate_support_resistance_levels(df, left_bars=15, right_bars=15):
    """
    Calculate support and resistance levels based on pivot points.
    
    Support levels are derived from pivot lows, resistance levels from pivot highs.
    Levels persist until a new pivot is found (similar to Pine Script's behavior).
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    left_bars : int
        Number of bars to look back for pivot detection (default: 15)
    right_bars : int
        Number of bars to look forward for pivot detection (default: 15)
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added columns:
        - 'resistance_level': Current resistance level (from pivot high)
        - 'support_level': Current support level (from pivot low)
    """
    df = df.copy()
    
    # Detect pivot points
    df = detect_pivot_high(df, left_bars=left_bars, right_bars=right_bars)
    df = detect_pivot_low(df, left_bars=left_bars, right_bars=right_bars)
    
    # Initialize level columns
    df['resistance_level'] = float('nan')
    df['support_level'] = float('nan')
    
    # Track current levels (forward fill until new pivot found)
    current_resistance = float('nan')
    current_support = float('nan')
    
    for i in range(len(df)):
        # Update resistance level if new pivot high found
        if not pd.isna(df.iloc[i]['pivot_high']):
            current_resistance = df.iloc[i]['pivot_high']
        
        # Update support level if new pivot low found
        if not pd.isna(df.iloc[i]['pivot_low']):
            current_support = df.iloc[i]['pivot_low']
        
        # Assign current levels (persist until new pivot)
        df.loc[df.index[i], 'resistance_level'] = current_resistance
        df.loc[df.index[i], 'support_level'] = current_support
    
    return df

def detect_sr_breaks(df, left_bars=15, right_bars=15, volume_threshold=20, show_breaks=True):
    """
    Detect support and resistance breaks with volume confirmation.
    
    Detects when price crosses above resistance or below support, with optional
    volume oscillator confirmation. Also detects wick patterns on breaks.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    left_bars : int
        Number of bars to look back for pivot detection (default: 15)
    right_bars : int
        Number of bars to look forward for pivot detection (default: 15)
    volume_threshold : float
        Minimum volume oscillator value for break confirmation (default: 20)
    show_breaks : bool
        Whether to detect and mark breaks (default: True)
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with added columns:
        - 'resistance_break': 1 when resistance broken with volume confirmation
        - 'support_break': 1 when support broken with volume confirmation
        - 'bull_wick_break': 1 when resistance broken with bull wick pattern
        - 'bear_wick_break': 1 when support broken with bear wick pattern
    """
    df = df.copy()
    
    # Calculate support/resistance levels
    df = calculate_support_resistance_levels(df, left_bars=left_bars, right_bars=right_bars)
    
    # Calculate volume oscillator
    df = calculate_volume_oscillator(df, fast_period=5, slow_period=10)
    
    # Initialize break columns
    df['resistance_break'] = 0
    df['support_break'] = 0
    df['bull_wick_break'] = 0
    df['bear_wick_break'] = 0
    
    if not show_breaks:
        return df
    
    # Detect breaks
    for i in range(1, len(df)):
        try:
            curr = df.iloc[i]
            prev = df.iloc[i-1]
            
            # Get current resistance and support levels
            resistance = curr['resistance_level']
            support = curr['support_level']
            volume_osc = curr['volume_osc']
            
            # Skip if no levels or volume data
            if pd.isna(resistance) and pd.isna(support):
                continue
            if pd.isna(volume_osc):
                continue
            
            # Resistance break detection
            # Crossover: close crosses above resistance level
            if not pd.isna(resistance):
                # Check for crossover (close crosses above resistance)
                if (prev['close'] <= resistance and curr['close'] > resistance):
                    # Check volume confirmation
                    if volume_osc > volume_threshold:
                        # Check for bull wick pattern
                        # Bull wick: open - low > close - open (long lower wick)
                        if not (curr['open'] - curr['low'] > curr['close'] - curr['open']):
                            # Regular break with volume
                            df.loc[df.index[i], 'resistance_break'] = 1
                        else:
                            # Bull wick break
                            df.loc[df.index[i], 'bull_wick_break'] = 1
                    # Even without volume, check for bull wick
                    elif curr['open'] - curr['low'] > curr['close'] - curr['open']:
                        df.loc[df.index[i], 'bull_wick_break'] = 1
            
            # Support break detection
            # Crossunder: close crosses below support level
            if not pd.isna(support):
                # Check for crossunder (close crosses below support)
                if (prev['close'] >= support and curr['close'] < support):
                    # Check volume confirmation
                    if volume_osc > volume_threshold:
                        # Check for bear wick pattern
                        # Bear wick: open - close < high - open (long upper wick)
                        if not (curr['open'] - curr['close'] < curr['high'] - curr['open']):
                            # Regular break with volume
                            df.loc[df.index[i], 'support_break'] = 1
                        else:
                            # Bear wick break
                            df.loc[df.index[i], 'bear_wick_break'] = 1
                    # Even without volume, check for bear wick
                    elif curr['open'] - curr['close'] < curr['high'] - curr['open']:
                        df.loc[df.index[i], 'bear_wick_break'] = 1
                        
        except (IndexError, KeyError):
            continue
    
    return df

