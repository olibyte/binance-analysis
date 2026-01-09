# Configure matplotlib to handle emoji characters properly
# Suppress font warnings for emojis - matplotlib will automatically fall back to fonts that support them
import matplotlib.pyplot as plt
import warnings
import pandas as pd
from calculations import (
    calculate_bollinger_bands, 
    calculate_k_envelopes,
    detect_sr_breaks,
    calculate_volume_oscillator,
    calculate_support_resistance_levels
)
from patterns import (
    detect_euphoria_pattern,
    detect_euphoria_with_k_envelopes,
    detect_euphoria_with_volume_confirmation,
    detect_euphoria_full_confluence,
    detect_marubozu,
    detect_three_candles,
    detect_three_methods,
    detect_tasuki,
    detect_hikkake,
    detect_quintuplets,
    detect_doji,
    detect_harami,
    detect_tweezers,
    detect_stick_sandwich,
    detect_hammer,
    detect_star,
    detect_piercing,
    detect_engulfing,
    detect_abandoned_baby,
    detect_spinning_top,
    detect_inside_up_down,
    detect_tower,
    detect_on_neck,
    detect_double_trouble,
    detect_bottle,
    detect_slingshot,
    detect_h_pattern,
    detect_doppelganger,
    detect_blockade,
    detect_barrier,
    detect_mirror,
    detect_shrinking
)

def plot_candlestick(df, title=None, num_candles=None, symbol=None, interval=None):
    """
    Plot candlestick chart from OHLC data.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data (columns: open, high, low, close)
    title : str
        Chart title (default: uses symbol and interval if provided)
    num_candles : int
        Number of recent candles to plot (default: all)
    symbol : str, optional
        Trading pair symbol (e.g., 'BTCUSDT') for title
    interval : str, optional
        Time interval (e.g., '15m', '1h') for title
    """
    # Select data to plot
    plot_data = df.tail(num_candles) if num_candles else df
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Determine colors for each candle (green for up, red for down)
    colors = ['green' if close >= open else 'red' 
              for close, open in zip(plot_data['close'], plot_data['open'])]
    
    # Plot the candlesticks
    for i, (idx, row) in enumerate(plot_data.iterrows()):
        open_price = row['open']
        high_price = row['high']
        low_price = row['low']
        close_price = row['close']
        
        # Determine color
        color = 'green' if close_price >= open_price else 'red'
        
        # Draw the wick (high-low line)
        ax.plot([i, i], [low_price, high_price], color='black', linewidth=0.5, alpha=0.7)
        
        # Draw the body (open-close rectangle)
        body_low = min(open_price, close_price)
        body_high = max(open_price, close_price)
        body_height = body_high - body_low
        
        # Use rectangle for the body
        rect = plt.Rectangle((i - 0.3, body_low), 0.6, body_height, 
                            facecolor=color, edgecolor='black', linewidth=0.5, alpha=0.8)
        ax.add_patch(rect)
    
    # Set labels and title
    if title is None:
        if symbol and interval:
            title = f'{symbol} - {interval} Candlestick Chart'
        else:
            title = 'Candlestick Chart'
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Price (USDT)', fontsize=12)
    
    # Format x-axis with dates
    num_labels = min(10, len(plot_data))  # Show max 10 date labels
    step = max(1, len(plot_data) // num_labels)
    tick_positions = range(0, len(plot_data), step)
    tick_labels = [plot_data.index[i].strftime('%Y-%m-%d %H:%M') for i in tick_positions]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha='right')
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='green', edgecolor='black', label='Bullish (Close ≥ Open)'),
        Patch(facecolor='red', edgecolor='black', label='Bearish (Close < Open)')
    ]
    ax.legend(handles=legend_elements, loc='upper left')
    
    plt.tight_layout()
    plt.show()
    
    # Print summary statistics
    print(f"\nChart Statistics:")
    print(f"Period: {plot_data.index[0]} to {plot_data.index[-1]}")
    print(f"Total Candles: {len(plot_data)}")
    print(f"Price Range: ${plot_data['low'].min():,.2f} - ${plot_data['high'].max():,.2f}")
    print(f"Current Price: ${plot_data['close'].iloc[-1]:,.2f}")
def plot_volume_chart(df, title=None, num_candles=None, fast_period=20, slow_period=50, symbol=None, interval=None):
    """
    Plot volume chart with moving averages, styled similar to trading platforms.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with volume and price data
    title : str
        Chart title (default: uses symbol and interval if provided)
    num_candles : int
        Number of recent candles to plot (default: all)
    fast_period : int
        Period for fast moving average (default: 20)
    slow_period : int
        Period for slow moving average (default: 50)
    symbol : str, optional
        Trading pair symbol (e.g., 'BTCUSDT') for title
    interval : str, optional
        Time interval (e.g., '15m', '1h') for title
    """
    # Select data to plot
    plot_data = df.tail(num_candles).copy() if num_candles else df.copy()
    
    # Calculate moving averages
    plot_data['vol_ma_fast'] = plot_data['volume'].rolling(window=fast_period).mean()
    plot_data['vol_ma_slow'] = plot_data['volume'].rolling(window=slow_period).mean()
    
    # Determine bar colors based on price direction
    bar_colors = ['#26a69a' if close >= open else '#ef5350' 
                  for close, open in zip(plot_data['close'], plot_data['open'])]
    
    # Create figure with dark theme
    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor('#1e1e1e')
    ax.set_facecolor('#1e1e1e')
    
    # Plot volume bars
    x_positions = range(len(plot_data))
    ax.bar(x_positions, plot_data['volume'], color=bar_colors, alpha=0.7, width=0.8)
    
    # Plot moving averages
    ax.plot(x_positions, plot_data['vol_ma_fast'], 
            color='#42a5f5', linewidth=1.5, label=f'MA({fast_period})', alpha=0.9)
    ax.plot(x_positions, plot_data['vol_ma_slow'], 
            color='#ef5350', linewidth=1.5, label=f'MA({slow_period})', alpha=0.9)
    
    # Format axes
    ax.set_facecolor('#1e1e1e')
    ax.tick_params(colors='#b0b0b0', labelsize=10)
    ax.spines['bottom'].set_color('#404040')
    ax.spines['top'].set_color('#404040')
    ax.spines['right'].set_color('#404040')
    ax.spines['left'].set_color('#404040')
    
    # Format x-axis with dates
    num_labels = min(10, len(plot_data))
    step = max(1, len(plot_data) // num_labels)
    tick_positions = range(0, len(plot_data), step)
    tick_labels = [plot_data.index[i].strftime('%Y-%m-%d %H:%M') for i in tick_positions]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha='right', color='#b0b0b0')
    
    # Set labels
    if title is None:
        if symbol:
            title = f'{symbol} - Volume Chart'
        else:
            title = 'Volume Chart'
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15, color='#ffffff')
    ax.set_ylabel('Volume', fontsize=11, color='#b0b0b0')
    ax.set_xlabel('Time', fontsize=11, color='#b0b0b0')
    
    # Add grid
    ax.grid(True, alpha=0.2, linestyle='--', color='#404040')
    ax.set_axisbelow(True)
    
    # Add volume metrics in top-left corner
    current_vol_btc = plot_data['volume'].iloc[-1]
    current_vol_usdt = plot_data['quote_volume'].iloc[-1]
    avg_vol_btc = plot_data['volume'].tail(20).mean()
    avg_vol_usdt = plot_data['quote_volume'].tail(20).mean()
    
    # Format volume values
    if current_vol_btc >= 1:
        vol_btc_str = f"{current_vol_btc:.2f}"
    else:
        vol_btc_str = f"{current_vol_btc:.4f}"
    
    if current_vol_usdt >= 1000:
        vol_usdt_str = f"{current_vol_usdt/1000:.3f}K"
    else:
        vol_usdt_str = f"{current_vol_usdt:.2f}"
    
    if avg_vol_btc >= 1:
        avg_vol_btc_str = f"{avg_vol_btc:.2f}"
    else:
        avg_vol_btc_str = f"{avg_vol_btc:.4f}"
    
    if avg_vol_usdt >= 1000:
        avg_vol_usdt_str = f"{avg_vol_usdt/1000:.3f}K"
    else:
        avg_vol_usdt_str = f"{avg_vol_usdt:.2f}"
    
    # Add text annotations
    textstr = f'Vol(BTC) {vol_btc_str}\nVol(USDT) {vol_usdt_str}\n{avg_vol_btc_str}\n{avg_vol_usdt_str}'
    props = dict(boxstyle='round', facecolor='#2d2d2d', alpha=0.8, edgecolor='#404040')
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', color='#b0b0b0', bbox=props, family='monospace')
    
    # Add legend
    ax.legend(loc='upper right', facecolor='#2d2d2d', edgecolor='#404040', 
              labelcolor='#b0b0b0', fontsize=9)
    
    plt.tight_layout()
    plt.show()
    
    # Print summary
    print(f"\nVolume Statistics:")
    print(f"Current Volume (BTC): {current_vol_btc:.4f}")
    print(f"Current Volume (USDT): {current_vol_usdt:,.2f}")
    print(f"Average Volume (BTC, last 20): {avg_vol_btc:.4f}")
    print(f"Average Volume (USDT, last 20): {avg_vol_usdt:,.2f}")

def plot_candlestick_with_bollinger(df, title=None, num_candles=None, period=20, num_std=2, symbol=None, interval=None):
    """
    Plot candlestick chart with Bollinger Bands overlay.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    title : str
        Chart title (default: uses symbol and interval if provided)
    num_candles : int
        Number of recent candles to plot (default: all)
    period : int
        Period for Bollinger Bands (default: 20)
    num_std : float
        Number of standard deviations for bands (default: 2)
    symbol : str, optional
        Trading pair symbol (e.g., 'BTCUSDT') for title
    interval : str, optional
        Time interval (e.g., '15m', '1h') for title
    """
    # Select data to plot
    plot_data = df.tail(num_candles).copy() if num_candles else df.copy()
    
    # Calculate Bollinger Bands
    plot_data = calculate_bollinger_bands(plot_data, period=period, num_std=num_std)
    
    # Get current/last candle data for header
    last_candle = plot_data.iloc[-1]
    current_time = plot_data.index[-1]
    open_price = last_candle['open']
    high_price = last_candle['high']
    low_price = last_candle['low']
    close_price = last_candle['close']
    change_pct = ((close_price - open_price) / open_price) * 100
    range_pct = ((high_price - low_price) / open_price) * 100
    
    # Get Bollinger Band values
    bb_upper = last_candle['bb_upper']
    bb_middle = last_candle['bb_middle']
    bb_lower = last_candle['bb_lower']
    
    # Create figure with dark theme
    fig = plt.figure(figsize=(16, 10))
    fig.patch.set_facecolor('#2d2d2d')
    
    # Create main chart area
    ax = plt.subplot(1, 1, 1)
    ax.set_facecolor('#1e1e1e')
    
    # Plot candlesticks
    x_positions = range(len(plot_data))
    for i, (idx, row) in enumerate(plot_data.iterrows()):
        open_price_candle = row['open']
        high_price_candle = row['high']
        low_price_candle = row['low']
        close_price_candle = row['close']
        
        # Determine color
        color = '#26a69a' if close_price_candle >= open_price_candle else '#ef5350'
        
        # Draw the wick (high-low line)
        ax.plot([i, i], [low_price_candle, high_price_candle], 
                color='#ffffff', linewidth=0.5, alpha=0.6)
        
        # Draw the body (open-close rectangle)
        body_low = min(open_price_candle, close_price_candle)
        body_high = max(open_price_candle, close_price_candle)
        body_height = body_high - body_low
        
        # Use rectangle for the body
        rect = plt.Rectangle((i - 0.3, body_low), 0.6, body_height, 
                            facecolor=color, edgecolor='#ffffff', linewidth=0.3, alpha=0.9)
        ax.add_patch(rect)
    
    # Plot Bollinger Bands
    ax.plot(x_positions, plot_data['bb_upper'], 
            color='#ab47bc', linewidth=1.5, label=f'Upper Band', alpha=0.8)
    ax.plot(x_positions, plot_data['bb_middle'], 
            color='#ec407a', linewidth=1.5, label=f'Middle Band (SMA{period})', alpha=0.8)
    ax.plot(x_positions, plot_data['bb_lower'], 
            color='#ab47bc', linewidth=1.5, label=f'Lower Band', alpha=0.8)
    
    # Fill area between bands
    ax.fill_between(x_positions, plot_data['bb_upper'], plot_data['bb_lower'], 
                    color='#ab47bc', alpha=0.1)
    
    # Format axes
    ax.tick_params(colors='#b0b0b0', labelsize=10)
    ax.spines['bottom'].set_color('#404040')
    ax.spines['top'].set_color('#404040')
    ax.spines['right'].set_color('#404040')
    ax.spines['left'].set_color('#404040')
    
    # Format x-axis with dates
    num_labels = min(12, len(plot_data))
    step = max(1, len(plot_data) // num_labels)
    tick_positions = range(0, len(plot_data), step)
    tick_labels = [plot_data.index[i].strftime('%Y/%m/%d %H:%M') for i in tick_positions]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha='right', color='#b0b0b0')
    
    # Set labels
    if title is None:
        if symbol and interval:
            title = f'{symbol} - {interval}'
        else:
            title = 'Candlestick Chart with Bollinger Bands'
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20, color='#ffffff')
    ax.set_ylabel('Price (USDT)', fontsize=12, color='#b0b0b0')
    ax.set_xlabel('Time', fontsize=12, color='#b0b0b0')
    
    # Add grid
    ax.grid(True, alpha=0.2, linestyle='--', color='#404040')
    ax.set_axisbelow(True)
    
    # Add header information box (top-left)
    header_text = (
        f"{current_time.strftime('%Y/%m/%d %H:%M')}\n"
        f"Open: {open_price:,.2f}\n"
        f"High: {high_price:,.2f}\n"
        f"Low: {low_price:,.2f}\n"
        f"Close: {close_price:,.2f}\n"
        f"CHANGE: {change_pct:.2f}%\n"
        f"Range: {range_pct:.2f}%\n"
        f"BOLL({period}, {num_std}):\n"
        f"UP: {bb_upper:,.2f}\n"
        f"MB: {bb_middle:,.2f}\n"
        f"DN: {bb_lower:,.2f}"
    )
    
    # Color code the values
    change_color = '#ef5350' if change_pct < 0 else '#26a69a'
    range_color = '#ef5350'
    
    props = dict(boxstyle='round', facecolor='#2d2d2d', alpha=0.95, 
                edgecolor='#404040', linewidth=1)
    ax.text(0.01, 0.99, header_text, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', color='#b0b0b0', bbox=props, 
            family='monospace', linespacing=1.3)
    
    # Highlight specific values with colors
    # Change percentage
    ax.text(0.01, 0.99 - 0.055, f"CHANGE: {change_pct:.2f}%", 
            transform=ax.transAxes, fontsize=9, color=change_color,
            family='monospace', weight='bold')
    # Range
    ax.text(0.01, 0.99 - 0.065, f"Range: {range_pct:.2f}%", 
            transform=ax.transAxes, fontsize=9, color=range_color,
            family='monospace', weight='bold')
    # Bollinger values
    ax.text(0.01, 0.99 - 0.085, f"UP: {bb_upper:,.2f}", 
            transform=ax.transAxes, fontsize=9, color='#ab47bc',
            family='monospace', weight='bold')
    ax.text(0.01, 0.99 - 0.095, f"MB: {bb_middle:,.2f}", 
            transform=ax.transAxes, fontsize=9, color='#ec407a',
            family='monospace', weight='bold')
    ax.text(0.01, 0.99 - 0.105, f"DN: {bb_lower:,.2f}", 
            transform=ax.transAxes, fontsize=9, color='#ab47bc',
            family='monospace', weight='bold')
    
    # Add legend
    ax.legend(loc='upper right', facecolor='#2d2d2d', edgecolor='#404040', 
              labelcolor='#b0b0b0', fontsize=9)
    
    plt.tight_layout()
    plt.show()
    
    # Print summary
    print(f"\nBollinger Bands Summary:")
    print(f"Period: {period}, Standard Deviations: {num_std}")
    print(f"Current Price: ${close_price:,.2f}")
    print(f"Upper Band: ${bb_upper:,.2f}")
    print(f"Middle Band (SMA{period}): ${bb_middle:,.2f}")
    print(f"Lower Band: ${bb_lower:,.2f}")
    print(f"Band Width: ${bb_upper - bb_lower:,.2f}")
    
def plot_candlestick_with_euphoria(df, title=None, num_candles=None, symbol=None, interval=None):
    """
    Plot candlestick chart with Euphoria pattern detection and marking.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    title : str
        Chart title (default: uses symbol and interval if provided)
    num_candles : int
        Number of recent candles to plot (default: all)
    symbol : str, optional
        Trading pair symbol (e.g., 'BTCUSDT') for title
    interval : str, optional
        Time interval (e.g., '15m', '1h') for title
    """
    # Select data to plot
    plot_data = df.tail(num_candles).copy() if num_candles else df.copy()
    
    # Detect Euphoria patterns
    plot_data = detect_euphoria_pattern(plot_data)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(16, 8))
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')
    
    # Plot candlesticks
    x_positions = range(len(plot_data))
    candle_width = 0.8  # Increased width to make candles closer together and easier to read
    
    for i, (idx, row) in enumerate(plot_data.iterrows()):
        open_price = row['open']
        high_price = row['high']
        low_price = row['low']
        close_price = row['close']
        
        # Determine color
        color = '#26a69a' if close_price >= open_price else '#ef5350'
        
        # Draw the wick (high-low line)
        ax.plot([i, i], [low_price, high_price], 
                color='black', linewidth=1, alpha=0.8)
        
        # Draw the body (open-close rectangle)
        body_low = min(open_price, close_price)
        body_high = max(open_price, close_price)
        body_height = body_high - body_low
        
        # Use rectangle for the body - wider candles for better readability
        rect = plt.Rectangle((i - candle_width/2, body_low), candle_width, body_height, 
                            facecolor=color, edgecolor='black', linewidth=0.5, alpha=1.0)
        ax.add_patch(rect)
        
        # Draw dashed vertical line on right side if Euphoria pattern detected
        if row['euphoria_bullish'] == 1 or row['euphoria_bearish'] == 1:
            # Draw dashed line along the right edge of the candle body
            ax.plot([i + candle_width/2, i + candle_width/2], [body_low, body_high], 
                   color='black', linewidth=1.5, linestyle='--', alpha=0.8)
    
    # Highlight Euphoria patterns with annotations
    euphoria_bullish_indices = plot_data[plot_data['euphoria_bullish'] == 1].index
    euphoria_bearish_indices = plot_data[plot_data['euphoria_bearish'] == 1].index
    
    for idx in euphoria_bullish_indices:
        i = plot_data.index.get_loc(idx)
        # Mark the pattern (no text annotation) - closer to candle
        # euphoria_bullish (three red candles) = contrarian → BUY signal → green upward triangle
        ax.scatter([i], [plot_data.loc[idx, 'high'] * 1.0005], 
                  marker='^', color='green', s=80, zorder=5)
    
    for idx in euphoria_bearish_indices:
        i = plot_data.index.get_loc(idx)
        # Mark the pattern (no text annotation) - closer to candle
        # euphoria_bearish (three green candles) = contrarian → SELL signal → red downward triangle
        ax.scatter([i], [plot_data.loc[idx, 'low'] * 0.9995], 
                  marker='v', color='red', s=80, zorder=5)
    
    # Format axes
    ax.tick_params(colors='black', labelsize=10)
    ax.spines['bottom'].set_color('black')
    ax.spines['top'].set_color('black')
    ax.spines['right'].set_color('black')
    ax.spines['left'].set_color('black')
    
    # Format x-axis with dates
    num_labels = min(15, len(plot_data))
    step = max(1, len(plot_data) // num_labels)
    tick_positions = range(0, len(plot_data), step)
    tick_labels = [plot_data.index[i].strftime('%Y-%m-%d %H:%M') for i in tick_positions]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha='right', color='black')
    
    # Set labels
    if title is None:
        if symbol and interval:
            title = f'{symbol} - {interval} - Euphoria Pattern Detection'
        else:
            title = 'Euphoria Pattern Detection'
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20, color='black')
    ax.set_ylabel('Price (USDT)', fontsize=12, color='black')
    ax.set_xlabel('Time', fontsize=12, color='black')
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--', color='gray')
    ax.set_axisbelow(True)
    
    # Determine current signal status
    # Check for most recent signals (within last few candles for active signal)
    lookback_period = 10  # Consider signals from last 10 candles as "active"
    recent_bullish = plot_data['euphoria_bullish'].tail(lookback_period).sum() > 0
    recent_bearish = plot_data['euphoria_bearish'].tail(lookback_period).sum() > 0
    
    # Find most recent signal
    last_bullish_idx = None
    last_bearish_idx = None
    
    if len(euphoria_bullish_indices) > 0:
        last_bullish_idx = euphoria_bullish_indices[-1]
    if len(euphoria_bearish_indices) > 0:
        last_bearish_idx = euphoria_bearish_indices[-1]
    
    # Determine which signal is more recent
    # Euphoria is contrarian:
    # - euphoria_bullish (three red candles) = contrarian bearish signal → BUY/LONG
    # - euphoria_bearish (three green candles) = contrarian bullish signal → SELL/SHORT
    signal_status = "NO SIGNAL"
    signal_color = '#808080'  # Gray
    signal_time = None
    signal_price = None
    
    if last_bullish_idx is not None and last_bearish_idx is not None:
        if last_bullish_idx > last_bearish_idx:
            # euphoria_bullish (red candles) → contrarian → BUY
            signal_status = "BUY SIGNAL"
            signal_color = '#26a69a'  # Green
            signal_time = last_bullish_idx
            signal_price = plot_data.loc[last_bullish_idx, 'close']
        else:
            # euphoria_bearish (green candles) → contrarian → SELL
            signal_status = "SELL SIGNAL"
            signal_color = '#ef5350'  # Red
            signal_time = last_bearish_idx
            signal_price = plot_data.loc[last_bearish_idx, 'close']
    elif last_bullish_idx is not None:
        # euphoria_bullish (red candles) → contrarian → BUY
        signal_status = "BUY SIGNAL"
        signal_color = '#26a69a'  # Green
        signal_time = last_bullish_idx
        signal_price = plot_data.loc[last_bullish_idx, 'close']
    elif last_bearish_idx is not None:
        # euphoria_bearish (green candles) → contrarian → SELL
        signal_status = "SELL SIGNAL"
        signal_color = '#ef5350'  # Red
        signal_time = last_bearish_idx
        signal_price = plot_data.loc[last_bearish_idx, 'close']
    
    # Add signal status box (top-right)
    if signal_time is not None:
        status_text = (
            f"Signal Status: {signal_status}\n"
            f"Time: {signal_time.strftime('%Y-%m-%d %H:%M')}\n"
            f"Price: ${signal_price:,.2f}"
        )
    else:
        status_text = f"Signal Status: {signal_status}"
    
    props = dict(boxstyle='round', facecolor='white', alpha=0.9, 
                edgecolor=signal_color, linewidth=2)
    ax.text(0.98, 0.98, status_text, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', horizontalalignment='right', 
            color=signal_color, bbox=props, family='monospace', 
            weight='bold', linespacing=1.4)
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#26a69a', edgecolor='black', label='Bullish Candle'),
        Patch(facecolor='#ef5350', edgecolor='black', label='Bearish Candle'),
        plt.Line2D([0], [0], color='black', linestyle='--', linewidth=1.5, label='Euphoria Pattern')
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
    
    plt.tight_layout()
    plt.show()
    
    # Print summary
    bullish_count = plot_data['euphoria_bullish'].sum()
    bearish_count = plot_data['euphoria_bearish'].sum()
    
    print(f"\nEuphoria Pattern Detection Summary:")
    print(f"Total Candles Analyzed: {len(plot_data)}")
    print(f"Bullish Euphoria Patterns (Bearish Signal): {int(bullish_count)}")
    print(f"Bearish Euphoria Patterns (Bullish Signal): {int(bearish_count)}")
    print(f"\nCurrent Signal Status: {signal_status}")
    if signal_time is not None:
        print(f"Last Signal Time: {signal_time}")
        print(f"Last Signal Price: ${signal_price:,.2f}")
    
    if bullish_count > 0:
        print(f"\nBullish Euphoria (Bearish Signal) detected at:")
        for idx in euphoria_bullish_indices:
            print(f"  - {idx}: Price = ${plot_data.loc[idx, 'close']:,.2f}")
    
    if bearish_count > 0:
        print(f"\nBearish Euphoria (Bullish Signal) detected at:")
        for idx in euphoria_bearish_indices:
            print(f"  - {idx}: Price = ${plot_data.loc[idx, 'close']:,.2f}")
            
def plot_k_envelopes_euphoria_signals(df, title=None, num_candles=None, lookback=800, symbol=None, interval=None):
    """
    Plot candlestick chart with K's Envelopes and Euphoria pattern signals.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    title : str
        Chart title (default: uses symbol and interval if provided)
    num_candles : int
        Number of recent candles to plot (default: all)
    lookback : int
        Period for K's envelopes (default: 800)
    symbol : str, optional
        Trading pair symbol (e.g., 'BTCUSDT') for title
    interval : str, optional
        Time interval (e.g., '15m', '1h') for title
    """
    # Select data to plot
    plot_data = df.tail(num_candles).copy() if num_candles else df.copy()
    
    # Detect signals with K's envelopes
    plot_data = detect_euphoria_with_k_envelopes(plot_data, lookback=lookback)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(18, 10))
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')
    
    # Plot candlesticks
    x_positions = range(len(plot_data))
    candle_width = 0.8
    
    for i, (idx, row) in enumerate(plot_data.iterrows()):
        open_price = row['open']
        high_price = row['high']
        low_price = row['low']
        close_price = row['close']
        
        # Determine color
        color = '#26a69a' if close_price >= open_price else '#ef5350'
        
        # Draw the wick (high-low line)
        ax.plot([i, i], [low_price, high_price], 
                color='black', linewidth=0.8, alpha=0.8)
        
        # Draw the body (open-close rectangle)
        body_low = min(open_price, close_price)
        body_high = max(open_price, close_price)
        body_height = body_high - body_low
        
        # Use rectangle for the body
        rect = plt.Rectangle((i - candle_width/2, body_low), candle_width, body_height, 
                            facecolor=color, edgecolor='black', linewidth=0.5, alpha=1.0)
        ax.add_patch(rect)
    
    # Plot K's Envelopes
    ax.plot(x_positions, plot_data['k_envelope_upper'], 
            color='#2196F3', linewidth=2, label=f'K\'s Upper Envelope ({lookback})', alpha=0.8, linestyle='--')
    ax.plot(x_positions, plot_data['k_envelope_lower'], 
            color='#2196F3', linewidth=2, label=f'K\'s Lower Envelope ({lookback})', alpha=0.8, linestyle='--')
    
    # Fill area between envelopes
    ax.fill_between(x_positions, plot_data['k_envelope_upper'], plot_data['k_envelope_lower'], 
                    color='#2196F3', alpha=0.1, label='K\'s Envelope Zone')
    
    # Mark buy signals (Long)
    buy_signals = plot_data[plot_data['buy_signal'] == 1]
    for idx in buy_signals.index:
        i = plot_data.index.get_loc(idx)
        price = plot_data.loc[idx, 'close']
        ax.scatter([i], [price], marker='^', color='green', s=200, zorder=5, 
                  edgecolors='darkgreen', linewidths=2, label='Long Signal' if i == buy_signals.index[0] else '')
        ax.annotate('LONG', xy=(i, price), xytext=(i, price * 1.02), 
                   ha='center', fontsize=9, color='green', weight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.7))
    
    # Mark sell signals (Short)
    sell_signals = plot_data[plot_data['sell_signal'] == -1]
    for idx in sell_signals.index:
        i = plot_data.index.get_loc(idx)
        price = plot_data.loc[idx, 'close']
        ax.scatter([i], [price], marker='v', color='red', s=200, zorder=5, 
                  edgecolors='darkred', linewidths=2, label='Short Signal' if i == sell_signals.index[0] else '')
        ax.annotate('SHORT', xy=(i, price), xytext=(i, price * 0.98), 
                   ha='center', fontsize=9, color='red', weight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcoral', alpha=0.7))
    
    # Format axes
    ax.tick_params(colors='black', labelsize=10)
    ax.spines['bottom'].set_color('black')
    ax.spines['top'].set_color('black')
    ax.spines['right'].set_color('black')
    ax.spines['left'].set_color('black')
    
    # Format x-axis with dates
    num_labels = min(15, len(plot_data))
    step = max(1, len(plot_data) // num_labels)
    tick_positions = range(0, len(plot_data), step)
    tick_labels = [plot_data.index[i].strftime('%Y-%m-%d %H:%M') for i in tick_positions]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha='right', color='black')
    
    # Set labels
    if title is None:
        if symbol and interval:
            title = f'{symbol} - {interval} - K\'s Envelopes + Euphoria Signals'
        else:
            title = 'K\'s Envelopes + Euphoria Signals'
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20, color='black')
    ax.set_ylabel('Price (USDT)', fontsize=12, color='black')
    ax.set_xlabel('Time', fontsize=12, color='black')
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--', color='gray')
    ax.set_axisbelow(True)
    
    # Determine current signal status
    last_buy_idx = buy_signals.index[-1] if len(buy_signals) > 0 else None
    last_sell_idx = sell_signals.index[-1] if len(sell_signals) > 0 else None
    
    signal_status = "NO SIGNAL"
    signal_color = '#808080'
    signal_time = None
    signal_price = None
    
    if last_buy_idx is not None and last_sell_idx is not None:
        if last_buy_idx > last_sell_idx:
            signal_status = "LONG SIGNAL"
            signal_color = '#26a69a'
            signal_time = last_buy_idx
            signal_price = plot_data.loc[last_buy_idx, 'close']
        else:
            signal_status = "SHORT SIGNAL"
            signal_color = '#ef5350'
            signal_time = last_sell_idx
            signal_price = plot_data.loc[last_sell_idx, 'close']
    elif last_buy_idx is not None:
        signal_status = "LONG SIGNAL"
        signal_color = '#26a69a'
        signal_time = last_buy_idx
        signal_price = plot_data.loc[last_buy_idx, 'close']
    elif last_sell_idx is not None:
        signal_status = "SHORT SIGNAL"
        signal_color = '#ef5350'
        signal_time = last_sell_idx
        signal_price = plot_data.loc[last_sell_idx, 'close']
    
    # Add signal status box (top-right)
    if signal_time is not None:
        status_text = (
            f"Signal Status: {signal_status}\n"
            f"Time: {signal_time.strftime('%Y-%m-%d %H:%M')}\n"
            f"Price: ${signal_price:,.2f}\n"
            f"K's Envelopes: {lookback} period"
        )
    else:
        status_text = (
            f"Signal Status: {signal_status}\n"
            f"K's Envelopes: {lookback} period"
        )
    
    props = dict(boxstyle='round', facecolor='white', alpha=0.9, 
                edgecolor=signal_color, linewidth=2)
    ax.text(0.98, 0.98, status_text, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', horizontalalignment='right', 
            color=signal_color, bbox=props, family='monospace', 
            weight='bold', linespacing=1.4)
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#26a69a', edgecolor='black', label='Bullish Candle'),
        Patch(facecolor='#ef5350', edgecolor='black', label='Bearish Candle'),
        plt.Line2D([0], [0], color='#2196F3', linestyle='--', linewidth=2, label='K\'s Envelopes'),
        plt.Line2D([0], [0], marker='^', color='w', markerfacecolor='green', 
                  markersize=10, label='Long Signal', markeredgecolor='darkgreen', markeredgewidth=2),
        plt.Line2D([0], [0], marker='v', color='w', markerfacecolor='red', 
                  markersize=10, label='Short Signal', markeredgecolor='darkred', markeredgewidth=2)
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
    
    plt.tight_layout()
    plt.show()
    
    # Print summary
    buy_count = plot_data['buy_signal'].sum()
    sell_count = abs(plot_data['sell_signal'].sum())
    
    print(f"\nK's Envelopes + Euphoria Pattern Signal Summary:")
    print(f"Total Candles Analyzed: {len(plot_data)}")
    print(f"K's Envelopes Period: {lookback}")
    print(f"Long Signals (Buy): {int(buy_count)}")
    print(f"Short Signals (Sell): {int(sell_count)}")
    print(f"\nCurrent Signal Status: {signal_status}")
    if signal_time is not None:
        print(f"Last Signal Time: {signal_time}")
        print(f"Last Signal Price: ${signal_price:,.2f}")
    
    if buy_count > 0:
        print(f"\nLong Signals detected at:")
        for idx in buy_signals.index:
            price = plot_data.loc[idx, 'close']
            upper = plot_data.loc[idx, 'k_envelope_upper']
            lower = plot_data.loc[idx, 'k_envelope_lower']
            print(f"  - {idx}: Price = ${price:,.2f} (Upper: ${upper:,.2f}, Lower: ${lower:,.2f})")
    
    if sell_count > 0:
        print(f"\nShort Signals detected at:")
        for idx in sell_signals.index:
            price = plot_data.loc[idx, 'close']
            upper = plot_data.loc[idx, 'k_envelope_upper']
            lower = plot_data.loc[idx, 'k_envelope_lower']
            print(f"  - {idx}: Price = ${price:,.2f} (Upper: ${upper:,.2f}, Lower: ${lower:,.2f})")
# Plot Chart with K's Envelopes, Euphoria Signals, and Volume Confirmation
def plot_euphoria_with_volume_confirmation(df, title=None, num_candles=None, lookback=800, symbol=None, interval=None):
    """
    Plot candlestick chart with K's Envelopes, Euphoria signals, and Volume confirmation.
    Uses subplots to show price action and volume separately.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    title : str
        Chart title (default: uses symbol and interval if provided)
    num_candles : int
        Number of recent candles to plot
    lookback : int
        Period for K's envelopes
    symbol : str, optional
        Trading pair symbol (e.g., 'BTCUSDT') for title
    interval : str, optional
        Time interval (e.g., '15m', '1h') for title
    """
    # Select data to plot
    plot_data = df.tail(num_candles).copy() if num_candles else df.copy()
    
    # Detect signals with volume confirmation
    plot_data = detect_euphoria_with_volume_confirmation(plot_data, lookback=lookback)
    
    # Create figure with subplots
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(3, 1, height_ratios=[3, 1, 0.5], hspace=0.3)
    
    # Main price chart
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor('#ffffff')
    
    # Volume chart
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    ax2.set_facecolor('#ffffff')
    
    # Plot candlesticks
    x_positions = range(len(plot_data))
    candle_width = 0.8
    
    for i, (idx, row) in enumerate(plot_data.iterrows()):
        open_price = row['open']
        high_price = row['high']
        low_price = row['low']
        close_price = row['close']
        
        # Determine color
        color = '#26a69a' if close_price >= open_price else '#ef5350'
        
        # Draw the wick
        ax1.plot([i, i], [low_price, high_price], 
                color='black', linewidth=0.8, alpha=0.8)
        
        # Draw the body
        body_low = min(open_price, close_price)
        body_high = max(open_price, close_price)
        body_height = body_high - body_low
        
        rect = plt.Rectangle((i - candle_width/2, body_low), candle_width, body_height, 
                            facecolor=color, edgecolor='black', linewidth=0.5, alpha=1.0)
        ax1.add_patch(rect)
    
    # Plot K's Envelopes
    ax1.plot(x_positions, plot_data['k_envelope_upper'], 
            color='#2196F3', linewidth=2, label=f'K\'s Upper Envelope ({lookback})', 
            alpha=0.8, linestyle='--')
    ax1.plot(x_positions, plot_data['k_envelope_lower'], 
            color='#2196F3', linewidth=2, label=f'K\'s Lower Envelope ({lookback})', 
            alpha=0.8, linestyle='--')
    ax1.fill_between(x_positions, plot_data['k_envelope_upper'], plot_data['k_envelope_lower'], 
                    color='#2196F3', alpha=0.1)
    
    # Mark signals - confirmed vs unconfirmed
    buy_signals = plot_data[plot_data['buy_signal'] == 1]
    buy_confirmed = plot_data[plot_data['buy_signal_confirmed'] == 1]
    sell_signals = plot_data[plot_data['sell_signal'] == -1]
    sell_confirmed = plot_data[plot_data['sell_signal_confirmed'] == -1]
    
    # Confirmed BUY signals (volume confirmed) - larger, brighter markers
    for idx in buy_confirmed.index:
        i = plot_data.index.get_loc(idx)
        price = plot_data.loc[idx, 'close']
        ax1.scatter([i], [price], marker='^', color='#00ff00', s=300, zorder=5, 
                  edgecolors='darkgreen', linewidths=3)
        ax1.annotate('LONG✓', xy=(i, price), xytext=(i, price * 1.02), 
                   ha='center', fontsize=10, color='darkgreen', weight='bold',
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='lightgreen', alpha=0.8))
    
    # Unconfirmed BUY signals - smaller, lighter markers
    for idx in buy_signals.index:
        if idx not in buy_confirmed.index:
            i = plot_data.index.get_loc(idx)
            price = plot_data.loc[idx, 'close']
            ax1.scatter([i], [price], marker='^', color='green', s=150, zorder=5, 
                      edgecolors='darkgreen', linewidths=1, alpha=0.6)
            ax1.annotate('LONG?', xy=(i, price), xytext=(i, price * 1.015), 
                       ha='center', fontsize=8, color='green', weight='normal',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.5))
    
    # Confirmed SELL signals (volume confirmed) - larger, brighter markers
    for idx in sell_confirmed.index:
        i = plot_data.index.get_loc(idx)
        price = plot_data.loc[idx, 'close']
        ax1.scatter([i], [price], marker='v', color='#ff0000', s=300, zorder=5, 
                  edgecolors='darkred', linewidths=3)
        ax1.annotate('SHORT✓', xy=(i, price), xytext=(i, price * 0.98), 
                   ha='center', fontsize=10, color='darkred', weight='bold',
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='lightcoral', alpha=0.8))
    
    # Unconfirmed SELL signals - smaller, lighter markers
    for idx in sell_signals.index:
        if idx not in sell_confirmed.index:
            i = plot_data.index.get_loc(idx)
            price = plot_data.loc[idx, 'close']
            ax1.scatter([i], [price], marker='v', color='red', s=150, zorder=5, 
                      edgecolors='darkred', linewidths=1, alpha=0.6)
            ax1.annotate('SHORT?', xy=(i, price), xytext=(i, price * 0.985), 
                       ha='center', fontsize=8, color='red', weight='normal',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcoral', alpha=0.5))
    
    # Format price chart
    ax1.tick_params(colors='black', labelsize=10)
    ax1.set_ylabel('Price (USDT)', fontsize=12, color='black', fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--', color='gray')
    ax1.set_axisbelow(True)
    
    # Format x-axis
    num_labels = min(15, len(plot_data))
    step = max(1, len(plot_data) // num_labels)
    tick_positions = range(0, len(plot_data), step)
    tick_labels = [plot_data.index[i].strftime('%Y-%m-%d %H:%M') for i in tick_positions]
    ax1.set_xticks(tick_positions)
    ax1.set_xticklabels(tick_labels, rotation=45, ha='right', color='black')
    
    if title is None:
        if symbol and interval:
            title = f'{symbol} - {interval} - Euphoria + K\'s Envelopes + Volume Confirmation'
        else:
            title = 'Euphoria + K\'s Envelopes + Volume Confirmation'
    ax1.set_title(title, fontsize=16, fontweight='bold', pad=20, color='black')
    
    # Plot volume bars
    bar_colors = ['#26a69a' if close >= open else '#ef5350' 
                  for close, open in zip(plot_data['close'], plot_data['open'])]
    ax2.bar(x_positions, plot_data['volume'], color=bar_colors, alpha=0.7, width=0.8)
    
    # Plot volume moving averages
    ax2.plot(x_positions, plot_data['vol_ma_fast'], 
            color='#42a5f5', linewidth=1.5, label='Vol MA(20)', alpha=0.9)
    ax2.plot(x_positions, plot_data['vol_ma_slow'], 
            color='#ef5350', linewidth=1.5, label='Vol MA(50)', alpha=0.9)
    
    # Highlight volume spikes on signal candles
    for idx in buy_confirmed.index.union(sell_confirmed.index):
        i = plot_data.index.get_loc(idx)
        if plot_data.loc[idx, 'volume_spike']:
            ax2.axvline(x=i, color='yellow', linestyle='--', alpha=0.5, linewidth=2)
    
    ax2.set_ylabel('Volume', fontsize=12, color='black', fontweight='bold')
    ax2.tick_params(colors='black', labelsize=10)
    ax2.grid(True, alpha=0.3, linestyle='--', color='gray')
    ax2.set_axisbelow(True)
    ax2.legend(loc='upper right', fontsize=9)
    
    # Signal status summary
    last_buy_confirmed = buy_confirmed.index[-1] if len(buy_confirmed) > 0 else None
    last_sell_confirmed = sell_confirmed.index[-1] if len(sell_confirmed) > 0 else None
    
    signal_status = "NO SIGNAL"
    signal_color = '#808080'
    signal_time = None
    signal_price = None
    
    if last_buy_confirmed is not None and last_sell_confirmed is not None:
        if last_buy_confirmed > last_sell_confirmed:
            signal_status = "LONG SIGNAL (CONFIRMED)"
            signal_color = '#00ff00'
            signal_time = last_buy_confirmed
            signal_price = plot_data.loc[last_buy_confirmed, 'close']
        else:
            signal_status = "SHORT SIGNAL (CONFIRMED)"
            signal_color = '#ff0000'
            signal_time = last_sell_confirmed
            signal_price = plot_data.loc[last_sell_confirmed, 'close']
    elif last_buy_confirmed is not None:
        signal_status = "LONG SIGNAL (CONFIRMED)"
        signal_color = '#00ff00'
        signal_time = last_buy_confirmed
        signal_price = plot_data.loc[last_buy_confirmed, 'close']
    elif last_sell_confirmed is not None:
        signal_status = "SHORT SIGNAL (CONFIRMED)"
        signal_color = '#ff0000'
        signal_time = last_sell_confirmed
        signal_price = plot_data.loc[last_sell_confirmed, 'close']
    
    # Add signal status box
    if signal_time is not None:
        status_text = (
            f"Signal Status: {signal_status}\n"
            f"Time: {signal_time.strftime('%Y-%m-%d %H:%M')}\n"
            f"Price: ${signal_price:,.2f}\n"
            f"Volume Confirmed: ✓"
        )
    else:
        status_text = (
            f"Signal Status: {signal_status}\n"
            f"Volume Confirmation: Required"
        )
    
    props = dict(boxstyle='round', facecolor='white', alpha=0.95, 
                edgecolor=signal_color, linewidth=3)
    ax1.text(0.98, 0.98, status_text, transform=ax1.transAxes, fontsize=11,
            verticalalignment='top', horizontalalignment='right', 
            color=signal_color, bbox=props, family='monospace', 
            weight='bold', linespacing=1.4)
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#26a69a', edgecolor='black', label='Bullish Candle'),
        Patch(facecolor='#ef5350', edgecolor='black', label='Bearish Candle'),
        plt.Line2D([0], [0], color='#2196F3', linestyle='--', linewidth=2, label='K\'s Envelopes'),
        plt.Line2D([0], [0], marker='^', color='w', markerfacecolor='#00ff00', 
                  markersize=12, label='Long (Confirmed)', markeredgecolor='darkgreen', markeredgewidth=2),
        plt.Line2D([0], [0], marker='^', color='w', markerfacecolor='green', 
                  markersize=8, label='Long (Unconfirmed)', markeredgecolor='darkgreen', markeredgewidth=1, alpha=0.6),
        plt.Line2D([0], [0], marker='v', color='w', markerfacecolor='#ff0000', 
                  markersize=12, label='Short (Confirmed)', markeredgecolor='darkred', markeredgewidth=2),
        plt.Line2D([0], [0], marker='v', color='w', markerfacecolor='red', 
                  markersize=8, label='Short (Unconfirmed)', markeredgecolor='darkred', markeredgewidth=1, alpha=0.6)
    ]
    ax1.legend(handles=legend_elements, loc='upper left', fontsize=9)
    
    plt.tight_layout()
    plt.show()
    
    # Print summary
    buy_total = plot_data['buy_signal'].sum()
    buy_confirmed_count = plot_data['buy_signal_confirmed'].sum()
    sell_total = abs(plot_data['sell_signal'].sum())
    sell_confirmed_count = abs(plot_data['sell_signal_confirmed'].sum())
    
    print(f"\nEuphoria + K's Envelopes + Volume Confirmation Summary:")
    print(f"Total Candles Analyzed: {len(plot_data)}")
    print(f"K's Envelopes Period: {lookback}")
    print(f"\nLong Signals:")
    print(f"  Total: {int(buy_total)}")
    print(f"  Volume Confirmed: {int(buy_confirmed_count)} ({int(buy_confirmed_count/buy_total*100) if buy_total > 0 else 0}%)")
    print(f"\nShort Signals:")
    print(f"  Total: {int(sell_total)}")
    print(f"  Volume Confirmed: {int(sell_confirmed_count)} ({int(sell_confirmed_count/sell_total*100) if sell_total > 0 else 0}%)")
    print(f"\nCurrent Signal Status: {signal_status}")
    if signal_time is not None:
        print(f"Last Confirmed Signal Time: {signal_time}")
        print(f"Last Confirmed Signal Price: ${signal_price:,.2f}")
# Plot Chart with Full Confluence (K's Envelopes + Volume + RSI)
def plot_euphoria_full_confluence(df, title=None, num_candles=None, lookback=800, rsi_period=14, 
                                    macd_fast=12, macd_slow=26, macd_signal=9, adx_period=14, symbol=None, interval=None):
    """
    Plot candlestick chart with full confluence: K's Envelopes + Volume + RSI + MACD + ADX.
    Uses multiple subplots to show price, volume, RSI, MACD, and ADX.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    title : str
        Chart title (default: uses symbol and interval if provided)
    num_candles : int
        Number of recent candles to plot
    lookback : int
        Period for K's envelopes
    rsi_period : int
        RSI period
    macd_fast : int
        MACD fast EMA period (default: 12)
    macd_slow : int
        MACD slow EMA period (default: 26)
    macd_signal : int
        MACD signal line EMA period (default: 9)
    adx_period : int
        ADX period (default: 14)
    symbol : str, optional
        Trading pair symbol (e.g., 'BTCUSDT') for title
    interval : str, optional
        Time interval (e.g., '15m', '1h') for title
    """    
    # Suppress font warnings for emoji characters
    # Matplotlib will automatically use font fallback to render emojis correctly
    warnings.filterwarnings('ignore', category=UserWarning, message='.*Glyph.*missing from font.*')
    warnings.filterwarnings('ignore', category=UserWarning, message='.*tight_layout.*')
    
    # Select data to plot
    plot_data = df.tail(num_candles).copy() if num_candles else df.copy()
    
    # Detect signals with full confluence (including MACD and ADX)
    plot_data = detect_euphoria_full_confluence(plot_data, lookback=lookback, rsi_period=rsi_period,
                                                 macd_fast=macd_fast, macd_slow=macd_slow, macd_signal=macd_signal,
                                                 adx_period=adx_period)
    
    # Create figure with subplots using constrained_layout for better compatibility
    fig = plt.figure(figsize=(22, 18), constrained_layout=True)
    gs = fig.add_gridspec(6, 1, height_ratios=[4, 1, 1, 1, 1, 0.3], hspace=0.25)
    
    # Main price chart
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor('#ffffff')
    
    # Volume chart
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    ax2.set_facecolor('#ffffff')
    
    # RSI chart
    ax3 = fig.add_subplot(gs[2], sharex=ax1)
    ax3.set_facecolor('#ffffff')
    
    # MACD chart
    ax4 = fig.add_subplot(gs[3], sharex=ax1)
    ax4.set_facecolor('#ffffff')
    
    # ADX chart
    ax5 = fig.add_subplot(gs[4], sharex=ax1)
    ax5.set_facecolor('#ffffff')
    
    # Plot candlesticks
    x_positions = range(len(plot_data))
    candle_width = 0.8
    
    for i, (idx, row) in enumerate(plot_data.iterrows()):
        open_price = row['open']
        high_price = row['high']
        low_price = row['low']
        close_price = row['close']
        
        color = '#26a69a' if close_price >= open_price else '#ef5350'
        
        ax1.plot([i, i], [low_price, high_price], 
                color='black', linewidth=0.8, alpha=0.8)
        
        body_low = min(open_price, close_price)
        body_high = max(open_price, close_price)
        body_height = body_high - body_low
        
        rect = plt.Rectangle((i - candle_width/2, body_low), candle_width, body_height, 
                            facecolor=color, edgecolor='black', linewidth=0.5, alpha=1.0)
        ax1.add_patch(rect)
    
    # Plot K's Envelopes
    ax1.plot(x_positions, plot_data['k_envelope_upper'], 
            color='#2196F3', linewidth=2, label=f'K\'s Upper ({lookback})', 
            alpha=0.8, linestyle='--')
    ax1.plot(x_positions, plot_data['k_envelope_lower'], 
            color='#2196F3', linewidth=2, label=f'K\'s Lower ({lookback})', 
            alpha=0.8, linestyle='--')
    ax1.fill_between(x_positions, plot_data['k_envelope_upper'], plot_data['k_envelope_lower'], 
                    color='#2196F3', alpha=0.1)
    
    # Mark signals by confluence level
    buy_highest = plot_data[plot_data['buy_signal_highest'] == 1]
    buy_high = plot_data[plot_data['buy_signal_high'] == 1]
    buy_medium = plot_data[plot_data['buy_signal_medium'] == 1]
    buy_low = plot_data[plot_data['buy_signal_low'] == 1]
    sell_highest = plot_data[plot_data['sell_signal_highest'] == -1]
    sell_high = plot_data[plot_data['sell_signal_high'] == -1]
    sell_medium = plot_data[plot_data['sell_signal_medium'] == -1]
    sell_low = plot_data[plot_data['sell_signal_low'] == -1]
    
    # Highest conviction BUY signals (all 4 confirmations)
    for idx in buy_highest.index:
        i = plot_data.index.get_loc(idx)
        price = plot_data.loc[idx, 'close']
        ax1.scatter([i], [price], marker='^', color='#00ff00', s=500, zorder=5, 
                  edgecolors='darkgreen', linewidths=5)
        ax1.annotate('LONG★★★★', xy=(i, price), xytext=(i, price * 1.03), 
                   ha='center', fontsize=12, color='darkgreen', weight='bold',
                   bbox=dict(boxstyle='round,pad=0.6', facecolor='lightgreen', alpha=0.95, edgecolor='darkgreen', linewidth=3))
    
    # High conviction BUY signals (3 of 4 confirmations)
    for idx in buy_high.index:
        i = plot_data.index.get_loc(idx)
        price = plot_data.loc[idx, 'close']
        ax1.scatter([i], [price], marker='^', color='#00ff00', s=400, zorder=5, 
                  edgecolors='darkgreen', linewidths=4)
        ax1.annotate('LONG★★★', xy=(i, price), xytext=(i, price * 1.025), 
                   ha='center', fontsize=11, color='darkgreen', weight='bold',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.9, edgecolor='darkgreen', linewidth=2))
    
    # Medium conviction BUY signals
    for idx in buy_medium.index:
        i = plot_data.index.get_loc(idx)
        price = plot_data.loc[idx, 'close']
        ax1.scatter([i], [price], marker='^', color='green', s=250, zorder=5, 
                  edgecolors='darkgreen', linewidths=2)
        ax1.annotate('LONG★★', xy=(i, price), xytext=(i, price * 1.02), 
                   ha='center', fontsize=9, color='green', weight='bold',
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='lightgreen', alpha=0.7))
    
    # Low conviction BUY signals
    for idx in buy_low.index:
        i = plot_data.index.get_loc(idx)
        price = plot_data.loc[idx, 'close']
        ax1.scatter([i], [price], marker='^', color='green', s=150, zorder=5, 
                  edgecolors='darkgreen', linewidths=1, alpha=0.5)
        ax1.annotate('LONG★', xy=(i, price), xytext=(i, price * 1.015), 
                   ha='center', fontsize=8, color='green', weight='normal',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.5))
    
    # Highest conviction SELL signals (all 4 confirmations)
    for idx in sell_highest.index:
        i = plot_data.index.get_loc(idx)
        price = plot_data.loc[idx, 'close']
        ax1.scatter([i], [price], marker='v', color='#ff0000', s=500, zorder=5, 
                  edgecolors='darkred', linewidths=5)
        ax1.annotate('SHORT★★★★', xy=(i, price), xytext=(i, price * 0.97), 
                   ha='center', fontsize=12, color='darkred', weight='bold',
                   bbox=dict(boxstyle='round,pad=0.6', facecolor='lightcoral', alpha=0.95, edgecolor='darkred', linewidth=3))
    
    # High conviction SELL signals (3 of 4 confirmations)
    for idx in sell_high.index:
        i = plot_data.index.get_loc(idx)
        price = plot_data.loc[idx, 'close']
        ax1.scatter([i], [price], marker='v', color='#ff0000', s=400, zorder=5, 
                  edgecolors='darkred', linewidths=4)
        ax1.annotate('SHORT★★★', xy=(i, price), xytext=(i, price * 0.975), 
                   ha='center', fontsize=11, color='darkred', weight='bold',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='lightcoral', alpha=0.9, edgecolor='darkred', linewidth=2))
    
    # Medium conviction SELL signals
    for idx in sell_medium.index:
        i = plot_data.index.get_loc(idx)
        price = plot_data.loc[idx, 'close']
        ax1.scatter([i], [price], marker='v', color='red', s=250, zorder=5, 
                  edgecolors='darkred', linewidths=2)
        ax1.annotate('SHORT★★', xy=(i, price), xytext=(i, price * 0.98), 
                   ha='center', fontsize=9, color='red', weight='bold',
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='lightcoral', alpha=0.7))
    
    # Low conviction SELL signals
    for idx in sell_low.index:
        i = plot_data.index.get_loc(idx)
        price = plot_data.loc[idx, 'close']
        ax1.scatter([i], [price], marker='v', color='red', s=150, zorder=5, 
                  edgecolors='darkred', linewidths=1, alpha=0.5)
        ax1.annotate('SHORT★', xy=(i, price), xytext=(i, price * 0.985), 
                   ha='center', fontsize=8, color='red', weight='normal',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcoral', alpha=0.5))
    
    # Mark RSI divergences on price chart (compact markers to avoid spacing issues)
    bearish_divs = plot_data[plot_data['bearish_divergence'] == True]
    bullish_divs = plot_data[plot_data['bullish_divergence'] == True]
    
    for idx in bearish_divs.index:
        i = plot_data.index.get_loc(idx)
        price = plot_data.loc[idx, 'high']
        ax1.text(i, price, 'd', ha='center', va='bottom', fontsize=12, 
                color='purple', alpha=0.9)
    
    for idx in bullish_divs.index:
        i = plot_data.index.get_loc(idx)
        price = plot_data.loc[idx, 'low']
        ax1.text(i, price, 'd', ha='center', va='top', fontsize=12, 
                color='blue', alpha=0.9)
    
    # Mark MACD divergences on price chart
    macd_bearish_divs = plot_data[plot_data['macd_bearish_divergence'] == True]
    macd_bullish_divs = plot_data[plot_data['macd_bullish_divergence'] == True]
    
    for idx in macd_bearish_divs.index:
        i = plot_data.index.get_loc(idx)
        price = plot_data.loc[idx, 'high']
        ax1.text(i, price, 'M', ha='center', va='bottom', fontsize=12, 
                color='orange', alpha=0.9)
    
    for idx in macd_bullish_divs.index:
        i = plot_data.index.get_loc(idx)
        price = plot_data.loc[idx, 'low']
        ax1.text(i, price, 'M', ha='center', va='top', fontsize=12, 
                color='cyan', alpha=0.9)
    
    # Format price chart
    ax1.tick_params(colors='black', labelsize=10)
    ax1.set_ylabel('Price (USDT)', fontsize=12, color='black', fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--', color='gray')
    ax1.set_axisbelow(True)
    
    if title is None:
        if symbol and interval:
            title = f'{symbol} - {interval} - Full Confluence (Euphoria + K\'s + Vol + RSI + MACD + ADX)'
        else:
            title = 'Full Confluence (Euphoria + K\'s + Vol + RSI + MACD + ADX)'
    ax1.set_title(title, fontsize=16, fontweight='bold', pad=20, color='black')
    
    # Plot volume
    bar_colors = ['#26a69a' if close >= open else '#ef5350' 
                  for close, open in zip(plot_data['close'], plot_data['open'])]
    ax2.bar(x_positions, plot_data['volume'], color=bar_colors, alpha=0.7, width=0.8)
    ax2.plot(x_positions, plot_data['vol_ma_fast'], 
            color='#42a5f5', linewidth=1.5, label='Vol MA(20)', alpha=0.9)
    ax2.plot(x_positions, plot_data['vol_ma_slow'], 
            color='#ef5350', linewidth=1.5, label='Vol MA(50)', alpha=0.9)
    ax2.set_ylabel('Volume', fontsize=11, color='black', fontweight='bold')
    ax2.tick_params(colors='black', labelsize=9)
    ax2.grid(True, alpha=0.3, linestyle='--', color='gray')
    ax2.set_axisbelow(True)
    ax2.legend(loc='upper right', fontsize=8)
    
    # Plot RSI
    ax3.plot(x_positions, plot_data['rsi'], color='#9c27b0', linewidth=2, label=f'RSI({rsi_period})')
    ax3.axhline(y=70, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='Overbought (70)')
    ax3.axhline(y=30, color='green', linestyle='--', linewidth=1.5, alpha=0.7, label='Oversold (30)')
    ax3.axhline(y=50, color='gray', linestyle=':', linewidth=1, alpha=0.5)
    ax3.fill_between(x_positions, 70, 100, color='red', alpha=0.1, label='Overbought Zone')
    ax3.fill_between(x_positions, 0, 30, color='green', alpha=0.1, label='Oversold Zone')
    ax3.set_ylabel('RSI', fontsize=11, color='black', fontweight='bold')
    ax3.set_ylim(0, 100)
    ax3.tick_params(colors='black', labelsize=9)
    ax3.grid(True, alpha=0.3, linestyle='--', color='gray')
    ax3.set_axisbelow(True)
    ax3.legend(loc='upper right', fontsize=8)
    
    # Plot MACD
    ax4.plot(x_positions, plot_data['macd'], color='#2196F3', linewidth=2, label=f'MACD({macd_fast},{macd_slow})')
    ax4.plot(x_positions, plot_data['macd_signal'], color='#FF9800', linewidth=2, label=f'Signal({macd_signal})')
    
    # Plot histogram (green for positive, red for negative)
    histogram_colors = ['#26a69a' if h >= 0 else '#ef5350' for h in plot_data['macd_histogram']]
    ax4.bar(x_positions, plot_data['macd_histogram'], color=histogram_colors, alpha=0.6, width=0.8, label='Histogram')
    
    # Mark zero line
    ax4.axhline(y=0, color='gray', linestyle='-', linewidth=1, alpha=0.5)
    
    # Mark crossovers
    for i in range(1, len(plot_data)):
        prev_macd = plot_data.iloc[i-1]['macd']
        prev_signal = plot_data.iloc[i-1]['macd_signal']
        curr_macd = plot_data.iloc[i]['macd']
        curr_signal = plot_data.iloc[i]['macd_signal']
        
        # Bearish crossover (MACD crosses below signal)
        if prev_macd > prev_signal and curr_macd < curr_signal:
            ax4.scatter([i], [curr_macd], marker='v', color='red', s=100, zorder=5, alpha=0.7)
        
        # Bullish crossover (MACD crosses above signal)
        if prev_macd < prev_signal and curr_macd > curr_signal:
            ax4.scatter([i], [curr_macd], marker='^', color='green', s=100, zorder=5, alpha=0.7)
    
    ax4.set_ylabel('MACD', fontsize=11, color='black', fontweight='bold')
    ax4.tick_params(colors='black', labelsize=9)
    ax4.grid(True, alpha=0.3, linestyle='--', color='gray')
    ax4.set_axisbelow(True)
    ax4.legend(loc='upper right', fontsize=8)
    
    # Plot ADX
    ax5.plot(x_positions, plot_data['adx'], color='#9c27b0', linewidth=2, label=f'ADX({adx_period})')
    ax5.plot(x_positions, plot_data['adx_plus_di'], color='#26a69a', linewidth=1.5, label='+DI', alpha=0.8)
    ax5.plot(x_positions, plot_data['adx_minus_di'], color='#ef5350', linewidth=1.5, label='-DI', alpha=0.8)
    
    # Add threshold lines
    ax5.axhline(y=20, color='orange', linestyle='--', linewidth=1.5, alpha=0.7, label='Weak Trend (20)')
    ax5.axhline(y=25, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='Strong Trend (25)')
    
    # Fill between +DI and -DI to show trend direction
    # Fill bullish areas where +DI > -DI
    bullish_mask = plot_data['adx_plus_di'] > plot_data['adx_minus_di']
    if bullish_mask.any():
        ax5.fill_between(x_positions, 
                        plot_data['adx_plus_di'].where(bullish_mask), 
                        plot_data['adx_minus_di'].where(bullish_mask),
                        color='#26a69a', alpha=0.2, label='Bullish Trend')
    
    # Fill bearish areas where -DI > +DI
    bearish_mask = plot_data['adx_minus_di'] > plot_data['adx_plus_di']
    if bearish_mask.any():
        ax5.fill_between(x_positions,
                        plot_data['adx_minus_di'].where(bearish_mask),
                        plot_data['adx_plus_di'].where(bearish_mask),
                        color='#ef5350', alpha=0.2, label='Bearish Trend')
    
    ax5.set_ylabel('ADX', fontsize=11, color='black', fontweight='bold')
    ax5.set_ylim(0, max(100, plot_data['adx'].max() * 1.1) if not plot_data['adx'].isna().all() else 100)
    ax5.tick_params(colors='black', labelsize=9)
    ax5.grid(True, alpha=0.3, linestyle='--', color='gray')
    ax5.set_axisbelow(True)
    ax5.legend(loc='upper right', fontsize=8)
    
    # Format x-axis with cleaner date formatting (similar to Binance)
    # Use a smarter approach: fewer labels with compact format
    num_labels = min(10, len(plot_data))  # Reduced from 15 to 10 for less crowding
    step = max(1, len(plot_data) // num_labels)
    tick_positions = range(0, len(plot_data), step)
    
    # Create smart labels: show date only when it changes, otherwise just time
    tick_labels = []
    prev_date = None
    for i in tick_positions:
        dt = plot_data.index[i]
        current_date = dt.date()
        
        if prev_date is None or current_date != prev_date:
            # Date changed: show "MM/DD HH:MM"
            tick_labels.append(dt.strftime('%m/%d %H:%M'))
        else:
            # Same date: show only "HH:MM"
            tick_labels.append(dt.strftime('%H:%M'))
        
        prev_date = current_date
    
    # Apply formatting with slight rotation to prevent overlap
    ax5.set_xticks(tick_positions)
    ax5.set_xticklabels(tick_labels, rotation=30, ha='right', color='black', fontsize=9)
    ax5.set_xlabel('Time', fontsize=12, color='black', fontweight='bold')
    
    # Also format the other axes (ax1, ax2, ax3, ax4) since they share the x-axis
    ax1.set_xticks(tick_positions)
    ax1.set_xticklabels([])  # Remove labels from top subplot to avoid duplication
    ax2.set_xticks(tick_positions)
    ax2.set_xticklabels([])  # Remove labels from middle subplot
    ax3.set_xticks(tick_positions)
    ax3.set_xticklabels([])  # Remove labels from RSI subplot
    ax4.set_xticks(tick_positions)
    ax4.set_xticklabels([])  # Remove labels from MACD subplot
    
    # Signal status
    all_buy = buy_highest.index.union(buy_high.index).union(buy_medium.index).union(buy_low.index)
    all_sell = sell_highest.index.union(sell_high.index).union(sell_medium.index).union(sell_low.index)
    
    last_buy = all_buy[-1] if len(all_buy) > 0 else None
    last_sell = all_sell[-1] if len(all_sell) > 0 else None
    
    signal_status = "NO SIGNAL"
    signal_color = '#808080'
    signal_time = None
    signal_price = None
    signal_confluence = ''
    
    if last_buy is not None and last_sell is not None:
        if last_buy > last_sell:
            signal_status = "LONG SIGNAL"
            signal_color = '#00ff00'
            signal_time = last_buy
            signal_price = plot_data.loc[last_buy, 'close']
            signal_confluence = plot_data.loc[last_buy, 'confluence_details']
        else:
            signal_status = "SHORT SIGNAL"
            signal_color = '#ff0000'
            signal_time = last_sell
            signal_price = plot_data.loc[last_sell, 'close']
            signal_confluence = plot_data.loc[last_sell, 'confluence_details']
    elif last_buy is not None:
        signal_status = "LONG SIGNAL"
        signal_color = '#00ff00'
        signal_time = last_buy
        signal_price = plot_data.loc[last_buy, 'close']
        signal_confluence = plot_data.loc[last_buy, 'confluence_details']
    elif last_sell is not None:
        signal_status = "SHORT SIGNAL"
        signal_color = '#ff0000'
        signal_time = last_sell
        signal_price = plot_data.loc[last_sell, 'close']
        signal_confluence = plot_data.loc[last_sell, 'confluence_details']
    
    # Add signal status box
    if signal_time is not None:
        status_text = (
            f"Signal: {signal_status}\n"
            f"Time: {signal_time.strftime('%Y-%m-%d %H:%M')}\n"
            f"Price: ${signal_price:,.2f}\n"
            f"Confluence: {signal_confluence}"
        )
    else:
        status_text = f"Signal: {signal_status}"
    
    props = dict(boxstyle='round', facecolor='white', alpha=0.95, 
                edgecolor=signal_color, linewidth=3)
    ax1.text(0.98, 0.98, status_text, transform=ax1.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right', 
            color=signal_color, bbox=props, family='monospace', 
            weight='bold', linespacing=1.4)
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#26a69a', edgecolor='black', label='Bullish Candle'),
        Patch(facecolor='#ef5350', edgecolor='black', label='Bearish Candle'),
        plt.Line2D([0], [0], color='#2196F3', linestyle='--', linewidth=2, label='K\'s Envelopes'),
        plt.Line2D([0], [0], marker='^', color='w', markerfacecolor='#00ff00', 
                  markersize=16, label='Long ★★★★ (Highest)', markeredgecolor='darkgreen', markeredgewidth=4),
        plt.Line2D([0], [0], marker='^', color='w', markerfacecolor='#00ff00', 
                  markersize=14, label='Long ★★★ (High)', markeredgecolor='darkgreen', markeredgewidth=3),
        plt.Line2D([0], [0], marker='^', color='w', markerfacecolor='green', 
                  markersize=10, label='Long ★★ (Medium)', markeredgecolor='darkgreen', markeredgewidth=2),
        plt.Line2D([0], [0], marker='^', color='w', markerfacecolor='green', 
                  markersize=7, label='Long ★ (Low)', markeredgecolor='darkgreen', markeredgewidth=1, alpha=0.5),
        plt.Line2D([0], [0], marker='v', color='w', markerfacecolor='#ff0000', 
                  markersize=16, label='Short ★★★★ (Highest)', markeredgecolor='darkred', markeredgewidth=4),
        plt.Line2D([0], [0], marker='v', color='w', markerfacecolor='#ff0000', 
                  markersize=14, label='Short ★★★ (High)', markeredgecolor='darkred', markeredgewidth=3),
        plt.Line2D([0], [0], marker='v', color='w', markerfacecolor='red', 
                  markersize=10, label='Short ★★ (Medium)', markeredgecolor='darkred', markeredgewidth=2),
        plt.Line2D([0], [0], marker='v', color='w', markerfacecolor='red', 
                  markersize=7, label='Short ★ (Low)', markeredgecolor='darkred', markeredgewidth=1, alpha=0.5)
    ]
    ax1.legend(handles=legend_elements, loc='upper left', fontsize=8)
    
    # Note: Using constrained_layout=True in figure creation instead of tight_layout()
    # This avoids warnings with complex GridSpec layouts
    plt.show()
    
    # Print summary
    buy_highest_count = plot_data['buy_signal_highest'].sum()
    buy_high_count = plot_data['buy_signal_high'].sum()
    buy_medium_count = plot_data['buy_signal_medium'].sum()
    buy_low_count = plot_data['buy_signal_low'].sum()
    sell_highest_count = abs(plot_data['sell_signal_highest'].sum())
    sell_high_count = abs(plot_data['sell_signal_high'].sum())
    sell_medium_count = abs(plot_data['sell_signal_medium'].sum())
    sell_low_count = abs(plot_data['sell_signal_low'].sum())
    
    print(f"\n{'='*70}")
    print(f"FULL CONFLUENCE SIGNAL SUMMARY")
    print(f"{'='*70}")
    print(f"Total Candles Analyzed: {len(plot_data)}")
    print(f"K's Envelopes Period: {lookback} | RSI Period: {rsi_period} | MACD: {macd_fast},{macd_slow},{macd_signal}")
    print(f"\nLONG SIGNALS:")
    print(f"  ★★★★ Highest Conviction (All 4): {int(buy_highest_count)}")
    print(f"  ★★★ High Conviction (3 of 4): {int(buy_high_count)}")
    print(f"  ★★ Medium Conviction (2 of 4): {int(buy_medium_count)}")
    print(f"  ★ Low Conviction (Env only): {int(buy_low_count)}")
    print(f"  Total: {int(buy_highest_count + buy_high_count + buy_medium_count + buy_low_count)}")
    print(f"\nSHORT SIGNALS:")
    print(f"  ★★★★ Highest Conviction (All 4): {int(sell_highest_count)}")
    print(f"  ★★★ High Conviction (3 of 4): {int(sell_high_count)}")
    print(f"  ★★ Medium Conviction (2 of 4): {int(sell_medium_count)}")
    print(f"  ★ Low Conviction (Env only): {int(sell_low_count)}")
    print(f"  Total: {int(sell_highest_count + sell_high_count + sell_medium_count + sell_low_count)}")
    print(f"\nCurrent Signal: {signal_status}")
    if signal_time is not None:
        print(f"  Time: {signal_time}")
        print(f"  Price: ${signal_price:,.2f}")
        print(f"  Confluence Level: {signal_confluence}")

# ============================================================================
# GENERIC PATTERN VISUALIZATION HELPER
# ============================================================================

def _plot_pattern_generic(df, pattern_name, detect_func, bullish_col, bearish_col, 
                          title=None, num_candles=None, symbol=None, interval=None, **pattern_params):
    """
    Generic helper function to plot any candlestick pattern.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    pattern_name : str
        Name of the pattern (for display)
    detect_func : function
        Pattern detection function
    bullish_col : str
        Column name for bullish pattern signals
    bearish_col : str
        Column name for bearish pattern signals
    title : str
        Chart title
    num_candles : int
        Number of recent candles to plot
    symbol : str
        Trading pair symbol
    interval : str
        Time interval
    **pattern_params : dict
        Pattern-specific parameters
    """
    # Select data to plot
    plot_data = df.tail(num_candles).copy() if num_candles else df.copy()
    
    # Detect pattern
    plot_data = detect_func(plot_data, **pattern_params)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(16, 8))
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')
    
    # Plot candlesticks
    x_positions = range(len(plot_data))
    candle_width = 0.8
    
    for i, (idx, row) in enumerate(plot_data.iterrows()):
        open_price = row['open']
        high_price = row['high']
        low_price = row['low']
        close_price = row['close']
        
        # Determine color
        color = '#26a69a' if close_price >= open_price else '#ef5350'
        
        # Draw the wick
        ax.plot([i, i], [low_price, high_price], 
                color='black', linewidth=1, alpha=0.8)
        
        # Draw the body
        body_low = min(open_price, close_price)
        body_high = max(open_price, close_price)
        body_height = body_high - body_low
        
        rect = plt.Rectangle((i - candle_width/2, body_low), candle_width, body_height, 
                            facecolor=color, edgecolor='black', linewidth=0.5, alpha=1.0)
        ax.add_patch(rect)
    
    # Mark pattern signals
    bullish_indices = plot_data[plot_data[bullish_col] == 1].index
    bearish_indices = plot_data[plot_data[bearish_col] == 1].index
    
    for idx in bullish_indices:
        i = plot_data.index.get_loc(idx)
        ax.scatter([i], [plot_data.loc[idx, 'high'] * 1.0005], 
                  marker='^', color='green', s=80, zorder=5)
    
    for idx in bearish_indices:
        i = plot_data.index.get_loc(idx)
        ax.scatter([i], [plot_data.loc[idx, 'low'] * 0.9995], 
                  marker='v', color='red', s=80, zorder=5)
    
    # Format axes
    ax.tick_params(colors='black', labelsize=10)
    ax.spines['bottom'].set_color('black')
    ax.spines['top'].set_color('black')
    ax.spines['right'].set_color('black')
    ax.spines['left'].set_color('black')
    
    # Format x-axis
    num_labels = min(15, len(plot_data))
    step = max(1, len(plot_data) // num_labels)
    tick_positions = range(0, len(plot_data), step)
    tick_labels = [plot_data.index[i].strftime('%Y-%m-%d %H:%M') for i in tick_positions]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha='right', color='black')
    
    # Set title and labels
    if title is None:
        if symbol and interval:
            title = f'{symbol} - {interval} - {pattern_name} Pattern'
        else:
            title = f'{pattern_name} Pattern Detection'
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20, color='black')
    ax.set_ylabel('Price (USDT)', fontsize=12, color='black')
    ax.set_xlabel('Time', fontsize=12, color='black')
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--', color='gray')
    ax.set_axisbelow(True)
    
    # Find most recent signal
    last_bullish_idx = bullish_indices[-1] if len(bullish_indices) > 0 else None
    last_bearish_idx = bearish_indices[-1] if len(bearish_indices) > 0 else None
    
    signal_status = "NO SIGNAL"
    signal_color = '#808080'
    signal_time = None
    signal_price = None
    
    if last_bullish_idx is not None and last_bearish_idx is not None:
        if last_bullish_idx > last_bearish_idx:
            signal_status = "BUY SIGNAL"
            signal_color = '#26a69a'
            signal_time = last_bullish_idx
            signal_price = plot_data.loc[last_bullish_idx, 'close']
        else:
            signal_status = "SELL SIGNAL"
            signal_color = '#ef5350'
            signal_time = last_bearish_idx
            signal_price = plot_data.loc[last_bearish_idx, 'close']
    elif last_bullish_idx is not None:
        signal_status = "BUY SIGNAL"
        signal_color = '#26a69a'
        signal_time = last_bullish_idx
        signal_price = plot_data.loc[last_bullish_idx, 'close']
    elif last_bearish_idx is not None:
        signal_status = "SELL SIGNAL"
        signal_color = '#ef5350'
        signal_time = last_bearish_idx
        signal_price = plot_data.loc[last_bearish_idx, 'close']
    
    # Add signal status box
    if signal_time is not None:
        status_text = (
            f"Signal Status: {signal_status}\n"
            f"Time: {signal_time.strftime('%Y-%m-%d %H:%M')}\n"
            f"Price: ${signal_price:,.2f}"
        )
    else:
        status_text = f"Signal Status: {signal_status}"
    
    props = dict(boxstyle='round', facecolor='white', alpha=0.9, 
                edgecolor=signal_color, linewidth=2)
    ax.text(0.98, 0.98, status_text, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', horizontalalignment='right', 
            color=signal_color, bbox=props, family='monospace', 
            weight='bold', linespacing=1.4)
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#26a69a', edgecolor='black', label='Bullish Candle'),
        Patch(facecolor='#ef5350', edgecolor='black', label='Bearish Candle'),
        plt.Line2D([0], [0], marker='^', color='green', linestyle='None', 
                  markersize=8, label='Buy Signal'),
        plt.Line2D([0], [0], marker='v', color='red', linestyle='None', 
                  markersize=8, label='Sell Signal')
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
    
    plt.tight_layout()
    plt.show()
    
    # Print summary
    bullish_count = plot_data[bullish_col].sum()
    bearish_count = plot_data[bearish_col].sum()
    
    print(f"\n{pattern_name} Pattern Detection Summary:")
    print(f"Total Candles Analyzed: {len(plot_data)}")
    print(f"Bullish Signals: {int(bullish_count)}")
    print(f"Bearish Signals: {int(bearish_count)}")
    print(f"\nCurrent Signal Status: {signal_status}")
    if signal_time is not None:
        print(f"Last Signal Time: {signal_time}")
        print(f"Last Signal Price: ${signal_price:,.2f}")
    
    if len(bullish_indices) > 0:
        print(f"\nBullish Signals detected at:")
        for idx in bullish_indices[-5:]:  # Show last 5
            print(f"  - {idx}: Price = ${plot_data.loc[idx, 'close']:,.2f}")
    
    if len(bearish_indices) > 0:
        print(f"\nBearish Signals detected at:")
        for idx in bearish_indices[-5:]:  # Show last 5
            print(f"  - {idx}: Price = ${plot_data.loc[idx, 'close']:,.2f}")

# ============================================================================
# INDIVIDUAL PATTERN VISUALIZATION FUNCTIONS
# ============================================================================

def plot_candlestick_with_marubozu(df, num_candles=200, symbol=None, interval=None):
    """Plot candlestick chart with Marubozu pattern signals."""
    _plot_pattern_generic(df, 'Marubozu', detect_marubozu, 'marubozu_bullish', 'marubozu_bearish',
                          num_candles=num_candles, symbol=symbol, interval=interval)

def plot_candlestick_with_three_candles(df, num_candles=200, body=0.0005, symbol=None, interval=None):
    """Plot candlestick chart with Three Candles pattern signals."""
    _plot_pattern_generic(df, 'Three Candles', detect_three_candles, 'three_candles_bullish', 'three_candles_bearish',
                          num_candles=num_candles, symbol=symbol, interval=interval, body=body)

def plot_candlestick_with_three_methods(df, num_candles=200, symbol=None, interval=None):
    """Plot candlestick chart with Three Methods pattern signals."""
    _plot_pattern_generic(df, 'Three Methods', detect_three_methods, 'three_methods_bullish', 'three_methods_bearish',
                          num_candles=num_candles, symbol=symbol, interval=interval)

def plot_candlestick_with_tasuki(df, num_candles=200, symbol=None, interval=None):
    """Plot candlestick chart with Tasuki pattern signals."""
    _plot_pattern_generic(df, 'Tasuki', detect_tasuki, 'tasuki_bullish', 'tasuki_bearish',
                          num_candles=num_candles, symbol=symbol, interval=interval)

def plot_candlestick_with_hikkake(df, num_candles=200, symbol=None, interval=None):
    """Plot candlestick chart with Hikkake pattern signals."""
    _plot_pattern_generic(df, 'Hikkake', detect_hikkake, 'hikkake_bullish', 'hikkake_bearish',
                          num_candles=num_candles, symbol=symbol, interval=interval)

def plot_candlestick_with_quintuplets(df, num_candles=200, body=0.0003, symbol=None, interval=None):
    """Plot candlestick chart with Quintuplets pattern signals."""
    _plot_pattern_generic(df, 'Quintuplets', detect_quintuplets, 'quintuplets_bullish', 'quintuplets_bearish',
                          num_candles=num_candles, symbol=symbol, interval=interval, body=body)

def plot_candlestick_with_doji(df, num_candles=200, symbol=None, interval=None):
    """Plot candlestick chart with Doji pattern signals."""
    _plot_pattern_generic(df, 'Doji', detect_doji, 'doji_bullish', 'doji_bearish',
                          num_candles=num_candles, symbol=symbol, interval=interval)

def plot_candlestick_with_harami(df, num_candles=200, symbol=None, interval=None):
    """Plot candlestick chart with Harami pattern signals."""
    _plot_pattern_generic(df, 'Harami', detect_harami, 'harami_bullish', 'harami_bearish',
                          num_candles=num_candles, symbol=symbol, interval=interval)

def plot_candlestick_with_tweezers(df, num_candles=200, body=0.0003, symbol=None, interval=None):
    """Plot candlestick chart with Tweezers pattern signals."""
    _plot_pattern_generic(df, 'Tweezers', detect_tweezers, 'tweezers_bullish', 'tweezers_bearish',
                          num_candles=num_candles, symbol=symbol, interval=interval, body=body)

def plot_candlestick_with_stick_sandwich(df, num_candles=200, symbol=None, interval=None):
    """Plot candlestick chart with Stick Sandwich pattern signals."""
    _plot_pattern_generic(df, 'Stick Sandwich', detect_stick_sandwich, 'stick_sandwich_bullish', 'stick_sandwich_bearish',
                          num_candles=num_candles, symbol=symbol, interval=interval)

def plot_candlestick_with_hammer(df, num_candles=200, body=0.0003, wick=0.0005, symbol=None, interval=None):
    """Plot candlestick chart with Hammer pattern signals."""
    _plot_pattern_generic(df, 'Hammer', detect_hammer, 'hammer_bullish', 'hammer_bearish',
                          num_candles=num_candles, symbol=symbol, interval=interval, body=body, wick=wick)

def plot_candlestick_with_star(df, num_candles=200, symbol=None, interval=None):
    """Plot candlestick chart with Star pattern signals."""
    _plot_pattern_generic(df, 'Star', detect_star, 'star_bullish', 'star_bearish',
                          num_candles=num_candles, symbol=symbol, interval=interval)

def plot_candlestick_with_piercing(df, num_candles=200, symbol=None, interval=None):
    """Plot candlestick chart with Piercing pattern signals."""
    _plot_pattern_generic(df, 'Piercing', detect_piercing, 'piercing_bullish', 'piercing_bearish',
                          num_candles=num_candles, symbol=symbol, interval=interval)

def plot_candlestick_with_engulfing(df, num_candles=200, symbol=None, interval=None):
    """Plot candlestick chart with Engulfing pattern signals."""
    _plot_pattern_generic(df, 'Engulfing', detect_engulfing, 'engulfing_bullish', 'engulfing_bearish',
                          num_candles=num_candles, symbol=symbol, interval=interval)

def plot_candlestick_with_abandoned_baby(df, num_candles=200, symbol=None, interval=None):
    """Plot candlestick chart with Abandoned Baby pattern signals."""
    _plot_pattern_generic(df, 'Abandoned Baby', detect_abandoned_baby, 'abandoned_baby_bullish', 'abandoned_baby_bearish',
                          num_candles=num_candles, symbol=symbol, interval=interval)

def plot_candlestick_with_spinning_top(df, num_candles=200, body=0.0003, wick=0.0003, symbol=None, interval=None):
    """Plot candlestick chart with Spinning Top pattern signals."""
    _plot_pattern_generic(df, 'Spinning Top', detect_spinning_top, 'spinning_top_bullish', 'spinning_top_bearish',
                          num_candles=num_candles, symbol=symbol, interval=interval, body=body, wick=wick)

def plot_candlestick_with_inside_up_down(df, num_candles=200, body=0.0003, symbol=None, interval=None):
    """Plot candlestick chart with Inside Up/Down pattern signals."""
    _plot_pattern_generic(df, 'Inside Up/Down', detect_inside_up_down, 'inside_up_down_bullish', 'inside_up_down_bearish',
                          num_candles=num_candles, symbol=symbol, interval=interval, body=body)

def plot_candlestick_with_tower(df, num_candles=200, body=0.0003, symbol=None, interval=None):
    """Plot candlestick chart with Tower pattern signals."""
    _plot_pattern_generic(df, 'Tower', detect_tower, 'tower_bullish', 'tower_bearish',
                          num_candles=num_candles, symbol=symbol, interval=interval, body=body)

def plot_candlestick_with_on_neck(df, num_candles=200, symbol=None, interval=None):
    """Plot candlestick chart with On Neck pattern signals."""
    _plot_pattern_generic(df, 'On Neck', detect_on_neck, 'on_neck_bullish', 'on_neck_bearish',
                          num_candles=num_candles, symbol=symbol, interval=interval)

def plot_candlestick_with_double_trouble(df, num_candles=200, atr_period=14, symbol=None, interval=None):
    """Plot candlestick chart with Double Trouble pattern signals."""
    _plot_pattern_generic(df, 'Double Trouble', detect_double_trouble, 'double_trouble_bullish', 'double_trouble_bearish',
                          num_candles=num_candles, symbol=symbol, interval=interval, atr_period=atr_period)

def plot_candlestick_with_bottle(df, num_candles=200, symbol=None, interval=None):
    """Plot candlestick chart with Bottle pattern signals."""
    _plot_pattern_generic(df, 'Bottle', detect_bottle, 'bottle_bullish', 'bottle_bearish',
                          num_candles=num_candles, symbol=symbol, interval=interval)

def plot_candlestick_with_slingshot(df, num_candles=200, symbol=None, interval=None):
    """Plot candlestick chart with Slingshot pattern signals."""
    _plot_pattern_generic(df, 'Slingshot', detect_slingshot, 'slingshot_bullish', 'slingshot_bearish',
                          num_candles=num_candles, symbol=symbol, interval=interval)

def plot_candlestick_with_h_pattern(df, num_candles=200, symbol=None, interval=None):
    """Plot candlestick chart with H Pattern signals."""
    _plot_pattern_generic(df, 'H Pattern', detect_h_pattern, 'h_pattern_bullish', 'h_pattern_bearish',
                          num_candles=num_candles, symbol=symbol, interval=interval)

def plot_candlestick_with_doppelganger(df, num_candles=200, symbol=None, interval=None):
    """Plot candlestick chart with Doppelgänger pattern signals."""
    _plot_pattern_generic(df, 'Doppelgänger', detect_doppelganger, 'doppelganger_bullish', 'doppelganger_bearish',
                          num_candles=num_candles, symbol=symbol, interval=interval)

def plot_candlestick_with_blockade(df, num_candles=200, symbol=None, interval=None):
    """Plot candlestick chart with Blockade pattern signals."""
    _plot_pattern_generic(df, 'Blockade', detect_blockade, 'blockade_bullish', 'blockade_bearish',
                          num_candles=num_candles, symbol=symbol, interval=interval)

def plot_candlestick_with_barrier(df, num_candles=200, symbol=None, interval=None):
    """Plot candlestick chart with Barrier pattern signals."""
    _plot_pattern_generic(df, 'Barrier', detect_barrier, 'barrier_bullish', 'barrier_bearish',
                          num_candles=num_candles, symbol=symbol, interval=interval)

def plot_candlestick_with_mirror(df, num_candles=200, symbol=None, interval=None):
    """Plot candlestick chart with Mirror pattern signals."""
    _plot_pattern_generic(df, 'Mirror', detect_mirror, 'mirror_bullish', 'mirror_bearish',
                          num_candles=num_candles, symbol=symbol, interval=interval)

def plot_candlestick_with_shrinking(df, num_candles=200, symbol=None, interval=None):
    """Plot candlestick chart with Shrinking pattern signals."""
    _plot_pattern_generic(df, 'Shrinking', detect_shrinking, 'shrinking_bullish', 'shrinking_bearish',
                          num_candles=num_candles, symbol=symbol, interval=interval)

# ============================================================================
# LUXALGO SUPPORT AND RESISTANCE LEVELS
# ============================================================================
# This work is licensed under a Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)
# https://creativecommons.org/licenses/by-nc-sa/4.0/
# © LuxAlgo

def _identify_level_segments(plot_data, level_column):
    """
    Identify continuous segments where a level is active.
    
    Parameters:
    -----------
    plot_data : pandas.DataFrame
        DataFrame with level data
    level_column : str
        Column name for the level ('resistance_level' or 'support_level')
    
    Returns:
    --------
    list of tuples
        List of (level_value, start_idx, end_idx) tuples representing segments
    """
    segments = []
    current_level = None
    start_idx = None
    
    for i, (idx, row) in enumerate(plot_data.iterrows()):
        level = row[level_column]
        
        if pd.isna(level):
            # End current segment if exists
            if current_level is not None:
                segments.append((current_level, start_idx, i - 1))
                current_level = None
                start_idx = None
        else:
            # Level is not NaN
            if current_level is None:
                # Starting a new segment
                current_level = level
                start_idx = i
            elif level != current_level:
                # Level changed - end previous segment, start new one
                segments.append((current_level, start_idx, i - 1))
                current_level = level
                start_idx = i
            # If level == current_level, continue the segment (do nothing)
    
    # Handle segment that extends to end
    if current_level is not None:
        segments.append((current_level, start_idx, len(plot_data) - 1))
    
    return segments

def _plot_sr_levels(ax, df, num_candles, left_bars, right_bars):
    """
    Helper function to plot support and resistance levels on price chart.
    
    Shows all historical levels spanning their active periods, with price labels
    only on current active levels (TradingView style).
    
    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        Axes object to plot on
    df : pandas.DataFrame
        DataFrame with support/resistance level data
    num_candles : int
        Number of candles to plot
    left_bars : int
        Left bars for pivot detection
    right_bars : int
        Right bars for pivot detection
    """
    plot_data = df.tail(num_candles) if num_candles else df
    
    # Identify all level segments (historical and current)
    resistance_segments = _identify_level_segments(plot_data, 'resistance_level')
    support_segments = _identify_level_segments(plot_data, 'support_level')
    
    # Get position for labels on the right side of the chart
    num_visible_candles = len(plot_data)
    last_idx = num_visible_candles - 1
    label_x = last_idx + num_visible_candles * 0.02
    
    # Track if we've added legend labels
    resistance_label_added = False
    support_label_added = False
    
    # Plot all resistance level segments
    for level, start_idx, end_idx in resistance_segments:
        is_current = (end_idx == last_idx)
        
        # Draw horizontal line spanning the active period
        ax.plot([start_idx, end_idx], [level, level], 
                color='#FF0000', linewidth=3, alpha=0.7, linestyle='-',
                label='Resistance' if not resistance_label_added else '')
        if not resistance_label_added:
            resistance_label_added = True
        
        # Add price label only if current active level (extends to right edge)
        if is_current:
            formatted_price = f'{level:,.2f}'
            ax.text(label_x, level, formatted_price, 
                    color='#FF0000', fontsize=10, fontweight='bold',
                    verticalalignment='center', horizontalalignment='left',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#FF0000', linewidth=1.5, alpha=0.9))
    
    # Plot all support level segments
    for level, start_idx, end_idx in support_segments:
        is_current = (end_idx == last_idx)
        
        # Draw horizontal line spanning the active period
        ax.plot([start_idx, end_idx], [level, level], 
                color='#233dee', linewidth=3, alpha=0.7, linestyle='-',
                label='Support' if not support_label_added else '')
        if not support_label_added:
            support_label_added = True
        
        # Add price label only if current active level (extends to right edge)
        if is_current:
            formatted_price = f'{level:,.2f}'
            ax.text(label_x, level, formatted_price,
                    color='#233dee', fontsize=10, fontweight='bold',
                    verticalalignment='center', horizontalalignment='left',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#233dee', linewidth=1.5, alpha=0.9))

def _plot_break_signals(ax, df, num_candles):
    """
    Helper function to plot break signals and wick patterns.
    
    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        Axes object to plot on
    df : pandas.DataFrame
        DataFrame with break signal data
    num_candles : int
        Number of candles to plot
    """
    plot_data = df.tail(num_candles) if num_candles else df
    start_idx = len(df) - len(plot_data)
    
    for i, (idx, row) in enumerate(plot_data.iterrows()):
        actual_idx = start_idx + i
        
        # Resistance breaks (green 'B' label)
        if row.get('resistance_break', 0) == 1:
            ax.scatter(i, row['high'], color='green', marker='^', s=200, zorder=5, edgecolors='white', linewidths=1)
            ax.annotate('B', xy=(i, row['high']), xytext=(i, row['high'] + (row['high'] - row['low']) * 0.02),
                       fontsize=10, fontweight='bold', color='white', ha='center', va='bottom',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='green', edgecolor='white', linewidth=1))
        
        # Support breaks (red 'B' label)
        if row.get('support_break', 0) == 1:
            ax.scatter(i, row['low'], color='red', marker='v', s=200, zorder=5, edgecolors='white', linewidths=1)
            ax.annotate('B', xy=(i, row['low']), xytext=(i, row['low'] - (row['high'] - row['low']) * 0.02),
                       fontsize=10, fontweight='bold', color='white', ha='center', va='top',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='red', edgecolor='white', linewidth=1))
        
        # Bull wick breaks
        if row.get('bull_wick_break', 0) == 1:
            ax.scatter(i, row['high'], color='green', marker='^', s=200, zorder=5, edgecolors='white', linewidths=1)
            ax.annotate('Bull Wick', xy=(i, row['high']), xytext=(i, row['high'] + (row['high'] - row['low']) * 0.02),
                       fontsize=9, fontweight='bold', color='white', ha='center', va='bottom',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='green', edgecolor='white', linewidth=1))
        
        # Bear wick breaks
        if row.get('bear_wick_break', 0) == 1:
            ax.scatter(i, row['low'], color='red', marker='v', s=200, zorder=5, edgecolors='white', linewidths=1)
            ax.annotate('Bear Wick', xy=(i, row['low']), xytext=(i, row['low'] - (row['high'] - row['low']) * 0.02),
                       fontsize=9, fontweight='bold', color='white', ha='center', va='top',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='red', edgecolor='white', linewidth=1))

def plot_candlestick_with_sr_levels(df, num_candles=200, left_bars=15, right_bars=15, 
                                    volume_threshold=20, show_breaks=True, symbol=None, interval=None):
    """
    Plot candlestick chart with LuxAlgo Support and Resistance Levels with Breaks.
    
    This indicator identifies pivot-based support and resistance levels and detects
    breaks with volume confirmation. Based on LuxAlgo's TradingView indicator.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data
    num_candles : int
        Number of recent candles to plot (default: 200)
    left_bars : int
        Number of bars to look back for pivot detection (default: 15)
    right_bars : int
        Number of bars to look forward for pivot detection (default: 15)
    volume_threshold : float
        Volume oscillator threshold for break confirmation (default: 20)
    show_breaks : bool
        Whether to show break signals (default: True)
    symbol : str, optional
        Trading pair symbol (e.g., 'BTCUSDT') for title
    interval : str, optional
        Time interval (e.g., '15m', '1h') for title
    """
    # Calculate support/resistance levels and breaks
    df_with_sr = detect_sr_breaks(df, left_bars=left_bars, right_bars=right_bars, 
                                   volume_threshold=volume_threshold, show_breaks=show_breaks)
    
    # Select data to plot
    plot_data = df_with_sr.tail(num_candles) if num_candles else df_with_sr
    
    # Create figure with subplots
    fig = plt.figure(figsize=(22, 14))
    gs = fig.add_gridspec(3, 1, height_ratios=[3, 1, 1], hspace=0.1)
    
    # Main price chart
    ax1 = fig.add_subplot(gs[0, 0])
    
    # Plot candlesticks
    for i, (idx, row) in enumerate(plot_data.iterrows()):
        open_price = row['open']
        high_price = row['high']
        low_price = row['low']
        close_price = row['close']
        
        color = 'green' if close_price >= open_price else 'red'
        
        # Draw wick
        ax1.plot([i, i], [low_price, high_price], color='black', linewidth=0.5, alpha=0.7)
        
        # Draw body
        body_low = min(open_price, close_price)
        body_high = max(open_price, close_price)
        body_height = body_high - body_low
        
        rect = plt.Rectangle((i - 0.3, body_low), 0.6, body_height,
                            facecolor=color, edgecolor='black', linewidth=0.5, alpha=0.8)
        ax1.add_patch(rect)
    
    # Plot support/resistance levels
    _plot_sr_levels(ax1, df_with_sr, num_candles, left_bars, right_bars)
    
    # Plot break signals
    if show_breaks:
        _plot_break_signals(ax1, df_with_sr, num_candles)
    
    # Format main chart
    if symbol and interval:
        title = f'{symbol} - {interval} - Support and Resistance Levels with Breaks [LuxAlgo]'
    else:
        title = 'Support and Resistance Levels with Breaks [LuxAlgo]'
    ax1.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax1.set_ylabel('Price (USDT)', fontsize=12)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(loc='upper left', fontsize=10)
    
    # Format x-axis
    num_labels = min(10, len(plot_data))
    step = max(1, len(plot_data) // num_labels)
    tick_positions = range(0, len(plot_data), step)
    tick_labels = [plot_data.index[i].strftime('%Y-%m-%d %H:%M') for i in tick_positions]
    
    # Volume chart
    ax2 = fig.add_subplot(gs[1, 0], sharex=ax1)
    colors_vol = ['green' if close >= open else 'red' 
                  for close, open in zip(plot_data['close'], plot_data['open'])]
    ax2.bar(range(len(plot_data)), plot_data['volume'], color=colors_vol, alpha=0.6, width=0.8)
    ax2.set_ylabel('Volume', fontsize=12)
    ax2.grid(True, alpha=0.3, linestyle='--')
    
    # Volume oscillator chart
    ax3 = fig.add_subplot(gs[2, 0], sharex=ax1)
    ax3.plot(range(len(plot_data)), plot_data['volume_osc'], color='purple', linewidth=2, label='Volume Oscillator')
    ax3.axhline(y=volume_threshold, color='orange', linestyle='--', linewidth=1.5, label=f'Threshold ({volume_threshold})')
    ax3.axhline(y=0, color='gray', linestyle='-', linewidth=0.5, alpha=0.5)
    ax3.fill_between(range(len(plot_data)), 0, plot_data['volume_osc'], 
                     where=(plot_data['volume_osc'] > volume_threshold), 
                     color='green', alpha=0.2, label='Volume Confirmed')
    ax3.set_ylabel('Volume Osc %', fontsize=12)
    ax3.set_xlabel('Time', fontsize=12)
    ax3.grid(True, alpha=0.3, linestyle='--')
    ax3.legend(loc='upper left', fontsize=9)
    
    # Set x-axis labels on bottom subplot only
    ax3.set_xticks(tick_positions)
    ax3.set_xticklabels(tick_labels, rotation=45, ha='right')
    
    plt.tight_layout()
    plt.show()
    
    # Print summary statistics
    print(f"\n{'='*80}")
    print(f"SUPPORT AND RESISTANCE LEVELS WITH BREAKS [LuxAlgo]")
    print(f"{'='*80}")
    print(f"Total Candles Analyzed: {len(plot_data)}")
    print(f"Pivot Detection: Left Bars={left_bars}, Right Bars={right_bars}")
    print(f"Volume Threshold: {volume_threshold}")
    
    # Count breaks
    resistance_breaks = plot_data['resistance_break'].sum()
    support_breaks = plot_data['support_break'].sum()
    bull_wick_breaks = plot_data['bull_wick_break'].sum()
    bear_wick_breaks = plot_data['bear_wick_break'].sum()
    
    print(f"\nBreak Signals:")
    print(f"  Resistance Breaks (with volume): {int(resistance_breaks)}")
    print(f"  Support Breaks (with volume): {int(support_breaks)}")
    print(f"  Bull Wick Breaks: {int(bull_wick_breaks)}")
    print(f"  Bear Wick Breaks: {int(bear_wick_breaks)}")
    
    # Current levels
    current_resistance = plot_data['resistance_level'].iloc[-1]
    current_support = plot_data['support_level'].iloc[-1]
    current_price = plot_data['close'].iloc[-1]
    
    print(f"\nCurrent Levels:")
    if not pd.isna(current_resistance):
        print(f"  Resistance: ${current_resistance:,.2f} (${current_resistance - current_price:,.2f} above price)")
    if not pd.isna(current_support):
        print(f"  Support: ${current_support:,.2f} (${current_price - current_support:,.2f} above price)")
    print(f"  Current Price: ${current_price:,.2f}")
    
    print(f"{'='*80}\n")
