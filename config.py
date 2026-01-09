"""
Configuration file for Binance trading analysis.

This module centralizes all configuration variables used across the project,
including API settings, trading pair configuration, chart display options,
and technical indicator parameters.
"""

# ============================================================================
# API Configuration
# ============================================================================
BASE_URL = "https://api.binance.com/api/v3/klines"
DEFAULT_LIMIT = 1500  # Maximum number of klines to fetch (Binance max: 1000 per request)

# Historical Data Collection Configuration
# ============================================================================
HISTORICAL_RATE_LIMIT_DELAY = 0.05  # Delay in seconds between API requests (default: 0.05s = 20 req/sec, well under 1200/min limit)
HISTORICAL_MAX_RETRIES = 3  # Maximum retry attempts for failed requests (default: 3)
HISTORICAL_CHUNK_SIZE = 1000  # Candles per chunk/request (default: 1000, Binance maximum)

# ============================================================================
# Trading Pair Configuration
# ============================================================================
SYMBOL = "BTCUSDT"  # Trading pair symbol (e.g., 'BTCUSDT', 'ETHUSDT')
INTERVAL = "1d"    # Time interval (1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M)

# ============================================================================
# Chart Display Configuration
# ============================================================================
DEFAULT_NUM_CANDLES = 150  # Default number of candles to display in charts
CHART_FIGSIZE = (22, 14)   # Default figure size for charts (width, height)

# ============================================================================
# Technical Indicator Defaults
# ============================================================================

# K's Envelopes
DEFAULT_LOOKBACK = 800  # Default period for K's Envelopes calculation

# RSI (Relative Strength Index)
DEFAULT_RSI_PERIOD = 14  # Default RSI period
RSI_OVERSOLD = 30         # RSI oversold threshold
RSI_OVERBOUGHT = 70       # RSI overbought threshold

# Volume Moving Averages
VOL_MA_FAST = 20  # Fast volume moving average period
VOL_MA_SLOW = 50  # Slow volume moving average period

# Bollinger Bands
BB_PERIOD = 20    # Bollinger Bands moving average period
BB_NUM_STD = 2    # Number of standard deviations for Bollinger Bands

# ============================================================================
# Pattern Detection Configuration
# ============================================================================
DIVERGENCE_LOOKBACK = 20  # Lookback period for RSI divergence detection
MIN_SWINGS = 2            # Minimum number of swings for divergence detection

# Take Profit and Stop Loss Configuration
# ============================================================================
DEFAULT_TAKE_PROFIT_PCT = 5.0  # Default take profit percentage from entry price
DEFAULT_STOP_LOSS_PCT = 3.0    # Default stop loss percentage from entry price

# Volume Participation Configuration
# ============================================================================
USE_VOLUME_PARTICIPATION = False  # Enable volume participation as confluence filter
VOLUME_PARTICIPATION_REQUIRED = False  # If True, only take trades with volume confirmation (strict mode)
VOLUME_SPIKE_THRESHOLD = 1.5  # Multiplier for volume spike detection (volume > threshold * fast MA)

# LuxAlgo Support/Resistance Configuration
# ============================================================================
# This work is licensed under a Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)
# https://creativecommons.org/licenses/by-nc-sa/4.0/
# © LuxAlgo
SR_LEFT_BARS = 15      # Left bars for pivot detection
SR_RIGHT_BARS = 15     # Right bars for pivot detection
SR_VOLUME_THRESHOLD = 20  # Volume oscillator threshold for break confirmation
SR_VOL_FAST = 5        # Fast EMA period for volume oscillator
SR_VOL_SLOW = 10       # Slow EMA period for volume oscillator

# ============================================================================
# Helper Functions
# ============================================================================

def get_chart_config():
    """
    Get configuration dictionary for chart plotting.
    
    Returns:
    --------
    dict : Configuration dictionary with symbol, interval, and num_candles
    """
    return {
        'symbol': SYMBOL,
        'interval': INTERVAL,
        'num_candles': DEFAULT_NUM_CANDLES
    }


def get_indicator_config():
    """
    Get configuration dictionary for technical indicators.
    
    Returns:
    --------
    dict : Configuration dictionary with all indicator parameters
    """
    return {
        'lookback': DEFAULT_LOOKBACK,
        'rsi_period': DEFAULT_RSI_PERIOD,
        'vol_ma_fast': VOL_MA_FAST,
        'vol_ma_slow': VOL_MA_SLOW,
        'bb_period': BB_PERIOD,
        'bb_num_std': BB_NUM_STD,
        'divergence_lookback': DIVERGENCE_LOOKBACK,
        'min_swings': MIN_SWINGS,
        'use_volume_participation': USE_VOLUME_PARTICIPATION,
        'volume_participation_required': VOLUME_PARTICIPATION_REQUIRED,
        'volume_spike_threshold': VOLUME_SPIKE_THRESHOLD
    }

