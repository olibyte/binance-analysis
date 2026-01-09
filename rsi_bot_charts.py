"""
RSI Trading Bot Charts Module

This module provides visualization functions for RSI trading bot backtest results.
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from calculations import calculate_rsi, calculate_volume_indicators


def plot_backtest_overview(results, df, num_candles=200, symbol=None, interval=None):
    """
    Plot comprehensive backtest overview with price, RSI, buy/sell signals, and equity curve.
    
    Parameters:
    -----------
    results : dict or Results object
        Backtest results from run_rsi_backtest() or Results object
    df : pandas.DataFrame
        Original DataFrame with OHLC data
    num_candles : int
        Number of recent candles to plot (default: 200)
    symbol : str, optional
        Trading pair symbol for title
    interval : str, optional
        Time interval for title
    """
    # Extract data
    if hasattr(results, 'data'):
        backtest_data = results.data
        trades_df = results.trades_df
        equity_history = results.equity_history
    else:
        backtest_data = results
        trades_df = backtest_data.get('trades_df', pd.DataFrame())
        equity_history = backtest_data.get('equity_history', pd.DataFrame())
    
    # Select data to plot
    plot_data = df.tail(num_candles).copy()
    
    # Calculate RSI for plotting
    rsi_period = backtest_data.get('config', {}).get('rsi_period', 14)
    plot_data = calculate_rsi(plot_data, period=rsi_period)
    
    # Detect divergence if enabled (for visualization)
    use_divergence = backtest_data.get('config', {}).get('use_divergence', True)
    divergence_lookback = backtest_data.get('config', {}).get('divergence_lookback', 20)
    if use_divergence:
        from calculations import detect_rsi_divergence
        plot_data = detect_rsi_divergence(plot_data, lookback=divergence_lookback)
    
    # Check if volume participation is enabled
    use_volume = backtest_data.get('config', {}).get('use_volume_participation', False)
    
    # Create figure with subplots (add volume subplot if volume participation is enabled)
    if use_volume:
        fig = plt.figure(figsize=(20, 16))
        gs = fig.add_gridspec(5, 1, height_ratios=[3, 1, 1, 1, 1], hspace=0.3)
    else:
        fig = plt.figure(figsize=(20, 14))
        gs = fig.add_gridspec(4, 1, height_ratios=[3, 1, 1, 1], hspace=0.3)
    
    # Price chart with buy/sell signals
    ax1 = fig.add_subplot(gs[0])
    
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
    
    # Plot buy/sell signals with divergence markers
    if not trades_df.empty:
        # Filter trades within plot range
        plot_start = plot_data.index[0]
        plot_end = plot_data.index[-1]
        plot_trades = trades_df[(trades_df.index >= plot_start) & (trades_df.index <= plot_end)]
        
        # Separate trades by type, signal type, and volume participation
        buy_trades_rsi = plot_trades[(plot_trades['type'] == 'BUY') & 
                                    (plot_trades.get('signal_type', 'RSI_THRESHOLD') == 'RSI_THRESHOLD')]
        buy_trades_div = plot_trades[(plot_trades['type'] == 'BUY') & 
                                    (plot_trades.get('signal_type', '') == 'DIVERGENCE')]
        sell_trades_rsi = plot_trades[(plot_trades['type'] == 'SELL') & 
                                     (plot_trades.get('signal_type', 'RSI_THRESHOLD') == 'RSI_THRESHOLD')]
        sell_trades_div = plot_trades[(plot_trades['type'] == 'SELL') & 
                                      (plot_trades.get('signal_type', '') == 'DIVERGENCE')]
        
        # Plot RSI threshold buy signals
        for idx, trade in buy_trades_rsi.iterrows():
            if idx in plot_data.index:
                price_idx = plot_data.index.get_loc(idx)
                # Check volume participation for marker styling
                vol_confirmed = trade.get('volume_participation', None) if use_volume else None
                if vol_confirmed:
                    # Volume confirmed: larger, brighter marker
                    ax1.scatter(price_idx, trade['price'], color='green', marker='^', 
                               s=300, zorder=6, edgecolors='darkgreen', linewidths=2, 
                               label='Buy (RSI + Vol)', alpha=0.9)
                else:
                    # No volume or not using volume: standard marker
                    ax1.scatter(price_idx, trade['price'], color='green', marker='^', 
                               s=200, zorder=5, edgecolors='black', linewidths=1.5, 
                               label='Buy (RSI)', alpha=0.8)
        
        # Plot divergence buy signals
        for idx, trade in buy_trades_div.iterrows():
            if idx in plot_data.index:
                price_idx = plot_data.index.get_loc(idx)
                vol_confirmed = trade.get('volume_participation', None) if use_volume else None
                if vol_confirmed:
                    # Volume confirmed divergence: extra large, bright
                    ax1.scatter(price_idx, trade['price'], color='lime', marker='^', 
                               s=400, zorder=7, edgecolors='darkgreen', linewidths=2.5, 
                               label='Buy (Div + Vol)', alpha=1.0)
                else:
                    # Standard divergence marker
                    ax1.scatter(price_idx, trade['price'], color='lime', marker='^', 
                               s=300, zorder=6, edgecolors='darkgreen', linewidths=2, 
                               label='Buy (Divergence)', alpha=0.9)
        
        # Plot RSI threshold sell signals
        for idx, trade in sell_trades_rsi.iterrows():
            if idx in plot_data.index:
                price_idx = plot_data.index.get_loc(idx)
                vol_confirmed = trade.get('volume_participation', None) if use_volume else None
                if vol_confirmed:
                    # Volume confirmed: larger, brighter marker
                    ax1.scatter(price_idx, trade['price'], color='red', marker='v',
                               s=300, zorder=6, edgecolors='darkred', linewidths=2,
                               label='Sell (RSI + Vol)', alpha=0.9)
                else:
                    # Standard marker
                    ax1.scatter(price_idx, trade['price'], color='red', marker='v',
                               s=200, zorder=5, edgecolors='black', linewidths=1.5,
                               label='Sell (RSI)', alpha=0.8)
        
        # Plot divergence sell signals
        for idx, trade in sell_trades_div.iterrows():
            if idx in plot_data.index:
                price_idx = plot_data.index.get_loc(idx)
                vol_confirmed = trade.get('volume_participation', None) if use_volume else None
                if vol_confirmed:
                    # Volume confirmed divergence: extra large, bright
                    ax1.scatter(price_idx, trade['price'], color='orange', marker='v',
                               s=400, zorder=7, edgecolors='darkred', linewidths=2.5,
                               label='Sell (Div + Vol)', alpha=1.0)
                else:
                    # Standard divergence marker
                    ax1.scatter(price_idx, trade['price'], color='orange', marker='v',
                               s=300, zorder=6, edgecolors='darkred', linewidths=2,
                               label='Sell (Divergence)', alpha=0.9)
    
    # Format price chart
    title = f'RSI Trading Bot Backtest'
    if symbol and interval:
        title += f' - {symbol} {interval}'
    ax1.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax1.set_ylabel('Price (USDT)', fontsize=12)
    ax1.grid(True, alpha=0.3, linestyle='--')
    
    # Format x-axis
    num_labels = min(10, len(plot_data))
    step = max(1, len(plot_data) // num_labels)
    tick_positions = range(0, len(plot_data), step)
    tick_labels = [plot_data.index[i].strftime('%Y-%m-%d %H:%M') for i in tick_positions]
    ax1.set_xticks(tick_positions)
    ax1.set_xticklabels(tick_labels, rotation=45, ha='right')
    
    # Add legend (only show once)
    handles, labels = ax1.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax1.legend(by_label.values(), by_label.keys(), loc='upper left')
    
    # RSI subplot with divergence markers
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    ax2.plot(range(len(plot_data)), plot_data['rsi'], color='purple', linewidth=1.5, label='RSI')
    ax2.axhline(y=70, color='red', linestyle='--', linewidth=1, alpha=0.7, label='Overbought (70)')
    ax2.axhline(y=30, color='green', linestyle='--', linewidth=1, alpha=0.7, label='Oversold (30)')
    ax2.fill_between(range(len(plot_data)), 30, 70, alpha=0.1, color='gray')
    
    # Mark divergence points on RSI chart
    if use_divergence and 'bullish_divergence' in plot_data.columns:
        bullish_div_indices = [i for i, (idx, row) in enumerate(plot_data.iterrows()) 
                              if row.get('bullish_divergence', False)]
        if bullish_div_indices:
            bullish_div_rsi = [plot_data.iloc[i]['rsi'] for i in bullish_div_indices]
            ax2.scatter(bullish_div_indices, bullish_div_rsi, color='lime', marker='o',
                       s=100, zorder=5, edgecolors='darkgreen', linewidths=1.5,
                       label='Bullish Divergence', alpha=0.8)
        
        bearish_div_indices = [i for i, (idx, row) in enumerate(plot_data.iterrows()) 
                              if row.get('bearish_divergence', False)]
        if bearish_div_indices:
            bearish_div_rsi = [plot_data.iloc[i]['rsi'] for i in bearish_div_indices]
            ax2.scatter(bearish_div_indices, bearish_div_rsi, color='orange', marker='o',
                       s=100, zorder=5, edgecolors='darkred', linewidths=1.5,
                       label='Bearish Divergence', alpha=0.8)
    
    ax2.set_ylabel('RSI', fontsize=12)
    ax2.set_ylim(0, 100)
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.legend(loc='upper right')
    ax2.set_xticks(tick_positions)
    ax2.set_xticklabels(tick_labels, rotation=45, ha='right')
    
    # Equity curve
    ax3 = fig.add_subplot(gs[2], sharex=ax1)
    if not equity_history.empty:
        # Filter equity history to plot range
        plot_equity = equity_history[(equity_history.index >= plot_start) & 
                                     (equity_history.index <= plot_end)]
        if not plot_equity.empty:
            # Get indices for equity data
            equity_indices = [plot_data.index.get_loc(idx) for idx in plot_equity.index 
                            if idx in plot_data.index]
            equity_values = [plot_equity.loc[idx, 'equity'] for idx in plot_equity.index 
                           if idx in plot_data.index]
            
            if equity_indices:
                ax3.plot(equity_indices, equity_values, color='blue', linewidth=2, label='Equity')
                ax3.axhline(y=backtest_data['initial_capital'], color='gray', 
                           linestyle='--', linewidth=1, alpha=0.7, label='Initial Capital')
                ax3.set_ylabel('Equity (USD)', fontsize=12)
                ax3.grid(True, alpha=0.3, linestyle='--')
                ax3.legend(loc='upper left')
    
    ax3.set_xticks(tick_positions)
    ax3.set_xticklabels(tick_labels, rotation=45, ha='right')
    
    # Position size
    ax4 = fig.add_subplot(gs[3], sharex=ax1)
    if not equity_history.empty:
        plot_equity = equity_history[(equity_history.index >= plot_start) & 
                                     (equity_history.index <= plot_end)]
        if not plot_equity.empty and 'position_btc' in plot_equity.columns:
            position_indices = [plot_data.index.get_loc(idx) for idx in plot_equity.index 
                              if idx in plot_data.index]
            position_values = [plot_equity.loc[idx, 'position_btc'] for idx in plot_equity.index 
                             if idx in plot_data.index]
            
            if position_indices:
                ax4.fill_between(position_indices, 0, position_values, 
                                color='orange', alpha=0.5, label='BTC Position')
                ax4.set_ylabel('Position (BTC)', fontsize=12)
                ax4.grid(True, alpha=0.3, linestyle='--')
                ax4.legend(loc='upper left')
    
    ax4.set_xlabel('Time', fontsize=12)
    ax4.set_xticks(tick_positions)
    ax4.set_xticklabels(tick_labels, rotation=45, ha='right')
    
    # Volume subplot (if volume participation is enabled)
    if use_volume:
        ax5 = fig.add_subplot(gs[4], sharex=ax1)
        
        # Calculate volume indicators if not already present
        if 'vol_ma_fast' not in plot_data.columns:
            vol_fast = backtest_data.get('config', {}).get('vol_fast_period', 20)
            vol_slow = backtest_data.get('config', {}).get('vol_slow_period', 50)
            plot_data = calculate_volume_indicators(plot_data, fast_period=vol_fast, slow_period=vol_slow)
        
        # Plot volume bars
        colors = ['green' if plot_data.iloc[i]['close'] >= plot_data.iloc[i]['open'] else 'red' 
                  for i in range(len(plot_data))]
        ax5.bar(range(len(plot_data)), plot_data['volume'], color=colors, alpha=0.6, label='Volume')
        
        # Plot volume moving averages
        if 'vol_ma_fast' in plot_data.columns:
            ax5.plot(range(len(plot_data)), plot_data['vol_ma_fast'], 
                    color='blue', linewidth=1.5, label='Vol MA Fast', alpha=0.7)
        if 'vol_ma_slow' in plot_data.columns:
            ax5.plot(range(len(plot_data)), plot_data['vol_ma_slow'], 
                    color='orange', linewidth=1.5, label='Vol MA Slow', alpha=0.7)
        
        # Mark volume spikes at signal points
        if not trades_df.empty:
            for idx, trade in plot_trades.iterrows():
                if idx in plot_data.index and trade.get('volume_participation', None):
                    vol_idx = plot_data.index.get_loc(idx)
                    vol_value = plot_data.iloc[vol_idx]['volume']
                    ax5.scatter(vol_idx, vol_value, color='yellow', marker='*', 
                              s=200, zorder=5, edgecolors='black', linewidths=1,
                              label='Volume Spike', alpha=0.9)
        
        ax5.set_ylabel('Volume', fontsize=12)
        ax5.set_xlabel('Time', fontsize=12)
        ax5.grid(True, alpha=0.3, linestyle='--')
        ax5.legend(loc='upper right', fontsize=9)
        ax5.set_xticks(tick_positions)
        ax5.set_xticklabels(tick_labels, rotation=45, ha='right')
    else:
        ax4.set_xlabel('Time', fontsize=12)
    
    plt.tight_layout()
    plt.show()


def plot_trade_analysis(results):
    """
    Plot trade analysis including profit/loss distribution and cumulative returns.
    
    Parameters:
    -----------
    results : dict or Results object
        Backtest results from run_rsi_backtest() or Results object
    """
    # Extract data
    if hasattr(results, 'data'):
        trades_df = results.trades_df
        equity_history = results.equity_history
        backtest_data = results.data
    else:
        backtest_data = results
        trades_df = backtest_data.get('trades_df', pd.DataFrame())
        equity_history = backtest_data.get('equity_history', pd.DataFrame())
    
    if trades_df.empty:
        print("No trades to analyze.")
        return
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    
    # 1. Profit/Loss Distribution
    ax1 = axes[0, 0]
    sells = trades_df[trades_df['type'] == 'SELL']
    if not sells.empty and 'profit_loss' in sells.columns:
        profit_loss = sells['profit_loss'].dropna()
        if len(profit_loss) > 0:
            ax1.hist(profit_loss, bins=20, color='steelblue', edgecolor='black', alpha=0.7)
            ax1.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Break Even')
            ax1.axvline(x=profit_loss.mean(), color='green', linestyle='--', 
                       linewidth=2, label=f'Mean: ${profit_loss.mean():.2f}')
            ax1.set_xlabel('Profit/Loss (USD)', fontsize=12)
            ax1.set_ylabel('Frequency', fontsize=12)
            ax1.set_title('Profit/Loss Distribution', fontsize=14, fontweight='bold')
            ax1.legend()
            ax1.grid(True, alpha=0.3, linestyle='--')
    
    # 2. Cumulative Returns
    ax2 = axes[0, 1]
    if not equity_history.empty and 'equity' in equity_history.columns:
        initial_capital = backtest_data['initial_capital']
        cumulative_returns = ((equity_history['equity'] - initial_capital) / initial_capital) * 100
        ax2.plot(equity_history.index, cumulative_returns, color='blue', linewidth=2)
        ax2.axhline(y=0, color='gray', linestyle='--', linewidth=1, alpha=0.7)
        ax2.set_xlabel('Time', fontsize=12)
        ax2.set_ylabel('Cumulative Return (%)', fontsize=12)
        ax2.set_title('Cumulative Returns Over Time', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, linestyle='--')
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # 3. Trade Count by Type
    ax3 = axes[1, 0]
    if not trades_df.empty:
        trade_counts = trades_df['type'].value_counts()
        colors = ['green' if t == 'BUY' else 'red' for t in trade_counts.index]
        ax3.bar(trade_counts.index, trade_counts.values, color=colors, alpha=0.7, edgecolor='black')
        ax3.set_xlabel('Trade Type', fontsize=12)
        ax3.set_ylabel('Count', fontsize=12)
        ax3.set_title('Trade Count by Type', fontsize=14, fontweight='bold')
        ax3.grid(True, alpha=0.3, linestyle='--', axis='y')
        # Add value labels on bars
        for i, v in enumerate(trade_counts.values):
            ax3.text(i, v, str(v), ha='center', va='bottom', fontweight='bold')
    
    # 4. Win/Loss Analysis (with volume participation comparison if enabled)
    ax4 = axes[1, 1]
    
    # Check if volume participation is enabled
    use_volume = backtest_data.get('config', {}).get('use_volume_participation', False)
    
    if not sells.empty and 'profit_loss' in sells.columns:
        profit_loss = sells['profit_loss'].dropna()
        if len(profit_loss) > 0:
            wins = profit_loss[profit_loss > 0]
            losses = profit_loss[profit_loss < 0]
            break_even = profit_loss[profit_loss == 0]
            
            categories = []
            counts = []
            colors_list = []
            
            if len(wins) > 0:
                categories.append('Wins')
                counts.append(len(wins))
                colors_list.append('green')
            if len(losses) > 0:
                categories.append('Losses')
                counts.append(len(losses))
                colors_list.append('red')
            if len(break_even) > 0:
                categories.append('Break Even')
                counts.append(len(break_even))
                colors_list.append('gray')
            
            if categories:
                ax4.bar(categories, counts, color=colors_list, alpha=0.7, edgecolor='black')
                ax4.set_xlabel('Trade Outcome', fontsize=12)
                ax4.set_ylabel('Count', fontsize=12)
                ax4.set_title('Win/Loss Analysis', fontsize=14, fontweight='bold')
                ax4.grid(True, alpha=0.3, linestyle='--', axis='y')
                # Add value labels
                for i, v in enumerate(counts):
                    ax4.text(i, v, str(v), ha='center', va='bottom', fontweight='bold')
                
                # Add win rate text
                win_rate = (len(wins) / len(profit_loss)) * 100 if len(profit_loss) > 0 else 0
                win_rate_text = f'Win Rate: {win_rate:.1f}%'
                
                # Add volume participation comparison if enabled
                if use_volume and 'volume_participation' in sells.columns:
                    vol_confirmed = sells[sells['volume_participation'] == True]
                    vol_not_confirmed = sells[sells['volume_participation'] == False]
                    
                    if not vol_confirmed.empty and not vol_not_confirmed.empty:
                        vol_confirmed_wins = len(vol_confirmed[vol_confirmed['profit_loss'] > 0])
                        vol_confirmed_wr = (vol_confirmed_wins / len(vol_confirmed)) * 100
                        vol_not_confirmed_wins = len(vol_not_confirmed[vol_not_confirmed['profit_loss'] > 0])
                        vol_not_confirmed_wr = (vol_not_confirmed_wins / len(vol_not_confirmed)) * 100
                        
                        win_rate_text += f'\nVol Confirmed: {vol_confirmed_wr:.1f}% ({len(vol_confirmed)} trades)'
                        win_rate_text += f'\nNo Vol: {vol_not_confirmed_wr:.1f}% ({len(vol_not_confirmed)} trades)'
                
                ax4.text(0.5, 0.95, win_rate_text, 
                        transform=ax4.transAxes, ha='center', va='top',
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                        fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.show()
    
    # Print summary statistics
    print("\n" + "=" * 70)
    print("TRADE ANALYSIS SUMMARY")
    print("=" * 70)
    if not sells.empty and 'profit_loss' in sells.columns:
        profit_loss = sells['profit_loss'].dropna()
        if len(profit_loss) > 0:
            print(f"Total Completed Trades: {len(profit_loss)}")
            print(f"Winning Trades: {len(profit_loss[profit_loss > 0])}")
            print(f"Losing Trades: {len(profit_loss[profit_loss < 0])}")
            print(f"Win Rate: {(len(profit_loss[profit_loss > 0]) / len(profit_loss)) * 100:.2f}%")
            print(f"Average Profit/Loss: ${profit_loss.mean():,.2f}")
            print(f"Best Trade: ${profit_loss.max():,.2f}")
            print(f"Worst Trade: ${profit_loss.min():,.2f}")
            print(f"Total Profit/Loss: ${profit_loss.sum():,.2f}")
    print("=" * 70)

