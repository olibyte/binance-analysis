# Binance Analysis Project Guide

This document provides a comprehensive overview of the binance-analysis project structure, development workflows, and key conventions to follow when working with this codebase.

## Project Overview

The binance-analysis project is a cryptocurrency trading analysis tool with a focus on:
1. Candlestick pattern detection and visualization
2. Technical indicators and trading signals
3. Trading bot backtesting and performance analysis
4. Support/Resistance level detection

The project uses the Binance API to fetch historical price data and provides tools for technical analysis of cryptocurrency markets.

## Repository Structure

```
binance-analysis/
├── binance_analysis.ipynb      # Main Jupyter notebook for analysis
├── calculations.py             # Utility functions for financial calculations
├── charts.py                   # Chart generation and visualization
├── config.py                   # Configuration settings for the entire project
├── data.py                     # Data fetching and processing from Binance API
├── data_cache/                 # Directory for cached data
├── patterns.py                 # Candlestick pattern detection library
├── requirements.txt            # Python dependencies
├── rsi_bot_backtest.py         # RSI-based trading bot backtesting
├── rsi_bot_charts.py           # Visualization for RSI bot results
├── rsi_bot_results.py          # Results processing for RSI bot
├── setup_instructions.md       # Setup and installation guide
├── volume_bot_backtest.py      # Volume-based trading bot backtesting
├── volume_bot_charts.py        # Visualization for volume bot results
├── volume_bot_results.py       # Results processing for volume bot
└── Tools_engine.md             # Documentation for bias tool scoring system
```

## Key Python Modules

### config.py
Central configuration file containing all parameters used across the project:
- API settings
- Trading pair configuration
- Chart display options
- Technical indicator parameters
- Pattern detection settings

### data.py
Handles data acquisition and processing:
- Fetching klines (candlestick) data from Binance API
- Historical data collection with pagination
- Error handling and rate limiting
- TradingView signals integration
- Data caching and persistence

### patterns.py
Comprehensive library of candlestick pattern detection functions:
- Trend-Following Patterns (marubozu, three candles, etc.)
- Classic Contrarian Patterns (doji, harami, hammer, etc.)
- Modern Trend-Following Patterns (double trouble, bottle, etc.)
- Modern Contrarian Patterns (doppelganger, blockade, etc.)
- Special focus on the "Euphoria" pattern with multiple detection variants

### charts.py
Visualization functions for candlestick charts and indicators:
- OHLC candlestick plotting
- Volume visualization
- Technical indicator overlays
- Pattern highlighting

### calculations.py
Utility functions for technical analysis calculations:
- Technical indicators (RSI, MACD, ATR, etc.)
- Support/Resistance level identification
- Market condition analysis

## Trading Bot Modules

### RSI Bot
Implements a trading strategy based on RSI (Relative Strength Index):
- `rsi_bot_backtest.py`: Implementation of backtesting logic
- `rsi_bot_charts.py`: Visualization of backtesting results
- `rsi_bot_results.py`: Analysis of trading performance

### Volume Bot
Implements a breakout strategy based on volume spikes:
- `volume_bot_backtest.py`: Implementation of backtesting logic
- `volume_bot_charts.py`: Visualization of backtesting results
- `volume_bot_results.py`: Analysis of trading performance
- Rules defined in `volume_bot.md`

## Development Setup

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the Notebook
```bash
jupyter notebook
# Open binance_analysis.ipynb
```

### Data Fetching
```python
# Example code to fetch historical data
from data import fetch_historical_klines
import datetime

# Fetch last 90 days of 4-hour data for BTC/USDT
end_time = datetime.datetime.now()
start_time = end_time - datetime.timedelta(days=90)
symbol = "BTCUSDT"
interval = "4h"
klines = fetch_historical_klines(symbol, interval, start_time, end_time)
```

### Pattern Detection
```python
# Example code to detect patterns
import pandas as pd
from patterns import detect_euphoria_pattern

# Convert klines to DataFrame
df = pd.DataFrame(klines, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
df = df.astype({'open': float, 'high': float, 'low': float, 'close': float, 'volume': float})

# Detect pattern
df = detect_euphoria_pattern(df)
```

## Code Conventions

### Configuration Management
- All configuration parameters are centralized in `config.py`
- Access configuration via the getter functions like `get_chart_config()` and `get_indicator_config()`
- Avoid hardcoding values that should be configurable

### Data Processing
- Use pandas DataFrames for structured data
- Ensure proper type conversion when working with API responses
- Handle API errors and rate limiting appropriately
- Cache data when possible to reduce API calls

### Pattern Detection
- Pattern detection functions should:
  1. Take a DataFrame with OHLC data as input
  2. Add columns to the DataFrame indicating where patterns appear
  3. Return the modified DataFrame
  4. Support both bullish and bearish pattern variants
  5. Include optional parameters for fine-tuning

### Visualization
- Use matplotlib and seaborn for chart generation
- Follow the chart format established in `charts.py`
- Use appropriate colors for different indicators
- Include legends and labels for clarity

## Common Tasks

### Modifying Configuration
```python
# In config.py
# Update existing parameters
SYMBOL = "ETHUSDT"  # Change trading pair
INTERVAL = "1h"     # Change time interval
DEFAULT_RSI_PERIOD = 7  # Change RSI period
```

### Adding New Patterns
```python
# In patterns.py
def detect_new_pattern(df, param1=default1, param2=default2):
    """
    Detect a new candlestick pattern in price data.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC price data
    param1, param2 : parameters for detection
    
    Returns:
    --------
    pandas.DataFrame
        Input DataFrame with added columns for pattern signals
    """
    # Add detection logic here
    df['new_pattern_bullish'] = 0  # Initialize signal columns
    df['new_pattern_bearish'] = 0
    
    # Detection criteria
    # [implementation]
    
    return df
```

### Running Backtests
```python
# For RSI bot
from rsi_bot_backtest import run_backtest

# Configure parameters
params = {
    'symbol': 'BTCUSDT',
    'interval': '1h',
    'rsi_period': 14,
    'rsi_overbought': 70,
    'rsi_oversold': 30
}

# Run backtest
results = run_backtest(params)
```

## Notes
- The Binance API returns data in UTC timezone
- Default limit is 500 klines (maximum is 1000)
- All prices are in USDT (not USD)
- This is not financial advice