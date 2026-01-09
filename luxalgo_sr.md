# LuxAlgo Support and Resistance Levels with Breaks

**License:** This work is licensed under a Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)  
**Source:** https://creativecommons.org/licenses/by-nc-sa/4.0/  
**© LuxAlgo**

## Overview

The LuxAlgo Support and Resistance Levels with Breaks indicator identifies key price levels based on pivot points and detects when these levels are broken with volume confirmation. This implementation is based on the original TradingView Pine Script indicator by LuxAlgo.

### Key Features

- **Pivot-Based Level Detection**: Automatically identifies support and resistance levels using pivot highs and lows
- **Volume Confirmation**: Uses volume oscillator to confirm break validity
- **Break Signal Detection**: Identifies when price breaks through support/resistance with volume
- **Wick Pattern Recognition**: Detects bull and bear wick patterns on breaks
- **Dynamic Level Updates**: Levels persist until new pivots are found

## Algorithm Overview

### 1. Pivot Detection

The indicator uses pivot points to identify significant price levels:

- **Pivot High**: A high point where the price is the highest in a window of `left_bars + right_bars + 1` candles
- **Pivot Low**: A low point where the price is the lowest in a window of `left_bars + right_bars + 1` candles

**Formula:**
- Pivot High at index `i`: `high[i] == max(high[i-left_bars : i+right_bars+1])`
- Pivot Low at index `i`: `low[i] == min(low[i-left_bars : i+right_bars+1])`

### 2. Support and Resistance Levels

- **Resistance Levels**: Derived from pivot highs (red horizontal lines)
- **Support Levels**: Derived from pivot lows (blue horizontal lines)
- **Level Persistence**: Levels remain active until a new pivot is found
- **Historical Positioning**: Levels are plotted at the pivot point location (offset = `-(right_bars+1)`)

### 3. Volume Oscillator

The volume oscillator measures volume momentum:

**Formula:**
```
Volume Oscillator = 100 * (EMA(volume, fast) - EMA(volume, slow)) / EMA(volume, slow)
```

Where:
- `fast` = Fast EMA period (default: 5)
- `slow` = Slow EMA period (default: 10)

**Interpretation:**
- Positive values: Fast volume EMA > Slow volume EMA (increasing volume)
- Negative values: Fast volume EMA < Slow volume EMA (decreasing volume)
- Higher values indicate stronger volume participation

### 4. Break Detection

Breaks are detected when price crosses support/resistance levels with volume confirmation:

#### Resistance Break (Bullish)
- **Condition**: `close` crosses above `resistance_level`
- **Volume Confirmation**: `volume_osc > volume_threshold`
- **Signal**: Green 'B' label above the candle

#### Support Break (Bearish)
- **Condition**: `close` crosses below `support_level`
- **Volume Confirmation**: `volume_osc > volume_threshold`
- **Signal**: Red 'B' label below the candle

### 5. Wick Pattern Detection

Special wick patterns are identified on breaks:

#### Bull Wick Break
- **Condition**: Resistance break AND `open - low > close - open` (long lower wick)
- **Interpretation**: Strong rejection of lower prices, bullish momentum
- **Signal**: "Bull Wick" label

#### Bear Wick Break
- **Condition**: Support break AND `open - close < high - open` (long upper wick)
- **Interpretation**: Strong rejection of higher prices, bearish momentum
- **Signal**: "Bear Wick" label

## Implementation Details

### Function Reference

#### `detect_pivot_high(df, left_bars=15, right_bars=15)`

Detects pivot high points in price data.

**Parameters:**
- `df`: DataFrame with OHLC data (must have 'high' column)
- `left_bars`: Number of bars to look back (default: 15)
- `right_bars`: Number of bars to look forward (default: 15)

**Returns:**
- DataFrame with added 'pivot_high' column containing pivot high prices (NaN where no pivot detected)

**Example:**
```python
from calculations import detect_pivot_high

df = detect_pivot_high(df, left_bars=15, right_bars=15)
```

#### `detect_pivot_low(df, left_bars=15, right_bars=15)`

Detects pivot low points in price data.

**Parameters:**
- `df`: DataFrame with OHLC data (must have 'low' column)
- `left_bars`: Number of bars to look back (default: 15)
- `right_bars`: Number of bars to look forward (default: 15)

**Returns:**
- DataFrame with added 'pivot_low' column containing pivot low prices (NaN where no pivot detected)

**Example:**
```python
from calculations import detect_pivot_low

df = detect_pivot_low(df, left_bars=15, right_bars=15)
```

#### `calculate_volume_oscillator(df, fast_period=5, slow_period=10)`

Calculates volume oscillator using EMA-based volume analysis.

**Parameters:**
- `df`: DataFrame with volume data (must have 'volume' column)
- `fast_period`: Fast EMA period (default: 5)
- `slow_period`: Slow EMA period (default: 10)

**Returns:**
- DataFrame with added 'volume_osc' column

**Example:**
```python
from calculations import calculate_volume_oscillator

df = calculate_volume_oscillator(df, fast_period=5, slow_period=10)
```

#### `calculate_support_resistance_levels(df, left_bars=15, right_bars=15)`

Calculates support and resistance levels based on pivot points.

**Parameters:**
- `df`: DataFrame with OHLC data
- `left_bars`: Number of bars to look back for pivot detection (default: 15)
- `right_bars`: Number of bars to look forward for pivot detection (default: 15)

**Returns:**
- DataFrame with added columns:
  - `'resistance_level'`: Current resistance level (from pivot high)
  - `'support_level'`: Current support level (from pivot low)

**Example:**
```python
from calculations import calculate_support_resistance_levels

df = calculate_support_resistance_levels(df, left_bars=15, right_bars=15)
```

#### `detect_sr_breaks(df, left_bars=15, right_bars=15, volume_threshold=20, show_breaks=True)`

Detects support and resistance breaks with volume confirmation.

**Parameters:**
- `df`: DataFrame with OHLC data
- `left_bars`: Number of bars to look back for pivot detection (default: 15)
- `right_bars`: Number of bars to look forward for pivot detection (default: 15)
- `volume_threshold`: Minimum volume oscillator value for break confirmation (default: 20)
- `show_breaks`: Whether to detect and mark breaks (default: True)

**Returns:**
- DataFrame with added columns:
  - `'resistance_break'`: 1 when resistance broken with volume confirmation
  - `'support_break'`: 1 when support broken with volume confirmation
  - `'bull_wick_break'`: 1 when resistance broken with bull wick pattern
  - `'bear_wick_break'`: 1 when support broken with bear wick pattern
  - `'resistance_level'`: Current resistance level
  - `'support_level'`: Current support level
  - `'volume_osc'`: Volume oscillator value

**Example:**
```python
from calculations import detect_sr_breaks

df = detect_sr_breaks(df, left_bars=15, right_bars=15, volume_threshold=20)
```

#### `plot_candlestick_with_sr_levels(df, num_candles=200, left_bars=15, right_bars=15, volume_threshold=20, show_breaks=True, symbol=None, interval=None)`

Plots candlestick chart with LuxAlgo Support and Resistance Levels with Breaks.

**Parameters:**
- `df`: DataFrame with OHLC data
- `num_candles`: Number of recent candles to plot (default: 200)
- `left_bars`: Number of bars to look back for pivot detection (default: 15)
- `right_bars`: Number of bars to look forward for pivot detection (default: 15)
- `volume_threshold`: Volume oscillator threshold for break confirmation (default: 20)
- `show_breaks`: Whether to show break signals (default: True)
- `symbol`: Trading pair symbol (e.g., 'BTCUSDT') for title (optional)
- `interval`: Time interval (e.g., '15m', '1h') for title (optional)

**Example:**
```python
from charts import plot_candlestick_with_sr_levels

plot_candlestick_with_sr_levels(df, num_candles=200, left_bars=15, right_bars=15, 
                                 volume_threshold=20, symbol='BTCUSDT', interval='1h')
```

## Trading Logic

### Interpreting Support and Resistance Levels

1. **Strong Levels**: Levels that have been tested multiple times are more significant
2. **Recent Levels**: More recent pivot points may be more relevant than older ones
3. **Level Strength**: The number of touches and bounces at a level indicates its strength

### Break Signal Significance

#### Resistance Break (Bullish)
- **Meaning**: Price breaks above a resistance level with volume confirmation
- **Implication**: Potential continuation of upward momentum
- **Action**: Consider long positions, but wait for confirmation
- **Volume Requirement**: Higher volume oscillator values indicate stronger conviction

#### Support Break (Bearish)
- **Meaning**: Price breaks below a support level with volume confirmation
- **Implication**: Potential continuation of downward momentum
- **Action**: Consider short positions or exit long positions
- **Volume Requirement**: Higher volume oscillator values indicate stronger conviction

### Volume Confirmation Importance

Volume confirmation helps filter false breakouts:

- **High Volume Oscillator (> threshold)**: Strong break with high conviction
- **Low Volume Oscillator (< threshold)**: Weak break, may be false breakout
- **Volume Spike**: Sudden increase in volume oscillator indicates strong participation

### Wick Pattern Implications

#### Bull Wick on Resistance Break
- **Meaning**: Strong rejection of lower prices during the break
- **Implication**: Very bullish signal, buyers are aggressive
- **Action**: Strong buy signal, potential for significant upward move

#### Bear Wick on Support Break
- **Meaning**: Strong rejection of higher prices during the break
- **Implication**: Very bearish signal, sellers are aggressive
- **Action**: Strong sell signal, potential for significant downward move

## Code Examples

### Basic Usage

```python
import pandas as pd
from calculations import detect_sr_breaks
from charts import plot_candlestick_with_sr_levels

# Load your OHLC data
# df = ... (your DataFrame with 'open', 'high', 'low', 'close', 'volume' columns)

# Detect breaks with default parameters
df_with_breaks = detect_sr_breaks(df)

# Plot the chart
plot_candlestick_with_sr_levels(df_with_breaks, num_candles=200, 
                                symbol='BTCUSDT', interval='1h')
```

### Custom Parameter Configuration

```python
from calculations import detect_sr_breaks
from charts import plot_candlestick_with_sr_levels

# Use custom pivot detection parameters
df_with_breaks = detect_sr_breaks(df, left_bars=20, right_bars=20, volume_threshold=25)

# Plot with custom parameters
plot_candlestick_with_sr_levels(df_with_breaks, num_candles=300, 
                                left_bars=20, right_bars=20, volume_threshold=25,
                                symbol='ETHUSDT', interval='4h')
```

### Integration with Other Indicators

```python
from calculations import detect_sr_breaks, calculate_rsi, calculate_k_envelopes
from charts import plot_candlestick_with_sr_levels

# Calculate multiple indicators
df = calculate_rsi(df, period=14)
df = calculate_k_envelopes(df, lookback=800)
df = detect_sr_breaks(df, left_bars=15, right_bars=15)

# Analyze confluence
# Check if RSI confirms break direction
# Check if price is near K's envelopes when break occurs
```

### Accessing Break Signals Programmatically

```python
from calculations import detect_sr_breaks

df = detect_sr_breaks(df)

# Get all resistance breaks
resistance_breaks = df[df['resistance_break'] == 1]
print(f"Total resistance breaks: {len(resistance_breaks)}")

# Get all support breaks
support_breaks = df[df['support_break'] == 1]
print(f"Total support breaks: {len(support_breaks)}")

# Get breaks with volume confirmation
volume_confirmed = df[(df['resistance_break'] == 1) | (df['support_break'] == 1)]
print(f"Volume-confirmed breaks: {len(volume_confirmed)}")

# Get current levels
current_resistance = df['resistance_level'].iloc[-1]
current_support = df['support_level'].iloc[-1]
print(f"Current Resistance: ${current_resistance:,.2f}")
print(f"Current Support: ${current_support:,.2f}")
```

### Backtesting Considerations

When using this indicator for backtesting:

1. **Lookahead Bias**: Pivot detection requires `right_bars` future candles, so signals are delayed
2. **Level Persistence**: Levels persist until new pivots, which may cause signals on old levels
3. **Volume Confirmation**: Always check volume oscillator to filter false breakouts
4. **Entry Timing**: Consider entering on the candle after the break signal
5. **Stop Loss**: Place stops below support (for longs) or above resistance (for shorts)

**Example Backtest Setup:**
```python
from calculations import detect_sr_breaks

# Calculate breaks
df = detect_sr_breaks(df, left_bars=15, right_bars=15, volume_threshold=20)

# Entry logic: Enter on next candle after break signal
for i in range(1, len(df)):
    if df.iloc[i-1]['resistance_break'] == 1:
        # Enter long on next candle open
        entry_price = df.iloc[i]['open']
        # ... your backtest logic
    
    if df.iloc[i-1]['support_break'] == 1:
        # Enter short on next candle open
        entry_price = df.iloc[i]['open']
        # ... your backtest logic
```

## Configuration

Default parameters can be configured in `config.py`:

```python
# LuxAlgo Support/Resistance Configuration
SR_LEFT_BARS = 15      # Left bars for pivot detection
SR_RIGHT_BARS = 15     # Right bars for pivot detection
SR_VOLUME_THRESHOLD = 20  # Volume oscillator threshold for break confirmation
SR_VOL_FAST = 5        # Fast EMA period for volume oscillator
SR_VOL_SLOW = 10       # Slow EMA period for volume oscillator
```

## Parameter Tuning

### Pivot Detection Parameters

- **Larger `left_bars`/`right_bars`**: More significant pivots, fewer levels, less sensitive
- **Smaller `left_bars`/`right_bars`**: More pivots, more levels, more sensitive
- **Recommended**: Start with 15/15, adjust based on timeframe

### Volume Threshold

- **Higher threshold**: Fewer but higher-quality break signals
- **Lower threshold**: More break signals but may include false breakouts
- **Recommended**: Start with 20, adjust based on asset volatility

### Volume Oscillator Periods

- **Faster periods (e.g., 3/6)**: More reactive, more signals
- **Slower periods (e.g., 10/20)**: More stable, fewer signals
- **Recommended**: Default 5/10 works well for most timeframes

## Limitations and Considerations

1. **Lookahead Bias**: Pivot detection requires future candles, causing signal delay
2. **Level Persistence**: Old levels may remain active even after price has moved significantly
3. **False Breakouts**: Not all breaks result in sustained moves; use additional confirmation
4. **Timeframe Dependency**: Optimal parameters vary by timeframe and asset
5. **Volume Data Quality**: Requires reliable volume data for accurate oscillator calculation

## Integration with Existing Codebase

This indicator integrates seamlessly with the existing codebase:

- **Location**: Functions in `calculations.py`, plotting in `charts.py`
- **Dependencies**: Uses existing pandas/numpy infrastructure
- **Compatibility**: Works with all existing OHLC data formats
- **Notebook Integration**: Can be used in `binance_analysis.ipynb` alongside other indicators

## References

- Original Pine Script: LuxAlgo Support and Resistance Levels with Breaks
- License: CC BY-NC-SA 4.0
- Documentation: This implementation follows the original algorithm logic

## Version History

- **v1.0**: Initial implementation based on LuxAlgo Pine Script v4

