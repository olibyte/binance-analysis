"""
Volume Breakout Trading Bot Charts Module

This module provides visualization functions for volume breakout trading bot backtest results.
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from calculations import calculate_rsi


def plot_backtest_overview(results, df, num_candles=200, symbol=None, interval=None):
    """
    Plot comprehensive backtest overview with price, volume, RSI, buy/sell signals, and equity curve.
    
    Parameters:
    -----------
    results : dict or Results object
        Backtest results from run_volume_backtest() or Results object
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
    
    # Create figure with subplots
    fig = plt.figure(figsize=(20, 16))
    gs = fig.add_gridspec(5, 1, height_ratios=[3, 1, 1, 1, 1], hspace=0.3)
    
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
    
    # Plot buy/sell signals
    if not trades_df.empty:
        # Filter trades within plot range
        plot_start = plot_data.index[0]
        plot_end = plot_data.index[-1]
        plot_trades = trades_df[(trades_df.index >= plot_start) & (trades_df.index <= plot_end)]
        
        # Separate entry and exit trades
        entry_trades = plot_trades[plot_trades['signal_type'] == 'VOLUME_BREAKOUT']
        exit_trades = plot_trades[plot_trades['exit_reason'].notna()]
        
        # Plot entry signals (buy stops and sell stops)
        for idx, trade in entry_trades.iterrows():
            if idx in plot_data.index:
                price_idx = plot_data.index.get_loc(idx)
                if trade['type'] == 'BUY':
                    # Buy stop entry
                    ax1.scatter(price_idx, trade['price'], color='green', marker='^', 
                               s=300, zorder=6, edgecolors='darkgreen', linewidths=2, 
                               label='Buy Stop Entry', alpha=0.9)
                    # Draw stop loss and take profit lines
                    if 'stop_loss' in trade and not pd.isna(trade['stop_loss']):
                        ax1.axhline(y=trade['stop_loss'], color='red', linestyle='--', 
                                   linewidth=1, alpha=0.5, xmin=price_idx/len(plot_data), 
                                   xmax=min(1.0, (price_idx+10)/len(plot_data)))
                    if 'take_profit' in trade and not pd.isna(trade['take_profit']):
                        ax1.axhline(y=trade['take_profit'], color='green', linestyle='--', 
                                   linewidth=1, alpha=0.5, xmin=price_idx/len(plot_data), 
                                   xmax=min(1.0, (price_idx+10)/len(plot_data)))
                elif trade['type'] == 'SELL':
                    # Sell stop entry
                    ax1.scatter(price_idx, trade['price'], color='red', marker='v',
                               s=300, zorder=6, edgecolors='darkred', linewidths=2,
                               label='Sell Stop Entry', alpha=0.9)
                    # Draw stop loss and take profit lines
                    if 'stop_loss' in trade and not pd.isna(trade['stop_loss']):
                        ax1.axhline(y=trade['stop_loss'], color='red', linestyle='--', 
                                   linewidth=1, alpha=0.5, xmin=price_idx/len(plot_data), 
                                   xmax=min(1.0, (price_idx+10)/len(plot_data)))
                    if 'take_profit' in trade and not pd.isna(trade['take_profit']):
                        ax1.axhline(y=trade['take_profit'], color='green', linestyle='--', 
                                   linewidth=1, alpha=0.5, xmin=price_idx/len(plot_data), 
                                   xmax=min(1.0, (price_idx+10)/len(plot_data)))
        
        # Plot exit signals
        for idx, trade in exit_trades.iterrows():
            if idx in plot_data.index:
                price_idx = plot_data.index.get_loc(idx)
                exit_reason = trade.get('exit_reason', '')
                profit_loss = trade.get('profit_loss', 0)
                
                if exit_reason == 'TAKE_PROFIT':
                    color = 'lime'
                    marker = 'o'
                    size = 200
                elif exit_reason == 'STOP_LOSS':
                    color = 'red'
                    marker = 'x'
                    size = 250
                else:  # MAX_HOLDING
                    color = 'orange'
                    marker = 's'
                    size = 150
                
                ax1.scatter(price_idx, trade['price'], color=color, marker=marker,
                           s=size, zorder=7, edgecolors='black', linewidths=1.5,
                           label=f'Exit ({exit_reason})', alpha=0.9)
    
    # Format price chart
    title = f'Volume Breakout Trading Bot Backtest'
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
    ax1.legend(by_label.values(), by_label.keys(), loc='upper left', fontsize=9)
    
    # Volume subplot
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    colors = ['green' if plot_data.iloc[i]['close'] >= plot_data.iloc[i]['open'] else 'red' 
              for i in range(len(plot_data))]
    ax2.bar(range(len(plot_data)), plot_data['volume'], color=colors, alpha=0.6, label='Volume')
    
    # Mark volume threshold
    volume_threshold = backtest_data.get('config', {}).get('volume_threshold_btc', 1.0)
    ax2.axhline(y=volume_threshold, color='orange', linestyle='--', linewidth=2, 
               alpha=0.7, label=f'Volume Threshold ({volume_threshold} BTC)')
    
    # Mark volume breakout signals
    if not trades_df.empty:
        for idx, trade in entry_trades.iterrows():
            if idx in plot_data.index:
                vol_idx = plot_data.index.get_loc(idx)
                vol_value = plot_data.iloc[vol_idx]['volume']
                ax2.scatter(vol_idx, vol_value, color='yellow', marker='*', 
                           s=300, zorder=5, edgecolors='black', linewidths=1.5,
                           label='Volume Breakout', alpha=0.9)
    
    ax2.set_ylabel('Volume (BTC)', fontsize=12)
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.legend(loc='upper right', fontsize=9)
    ax2.set_xticks(tick_positions)
    ax2.set_xticklabels(tick_labels, rotation=45, ha='right')
    
    # RSI subplot
    ax3 = fig.add_subplot(gs[2], sharex=ax1)
    ax3.plot(range(len(plot_data)), plot_data['rsi'], color='purple', linewidth=1.5, label='RSI')
    ax3.axhline(y=50, color='gray', linestyle='--', linewidth=2, alpha=0.7, label='RSI 50 (Filter Level)')
    ax3.axhline(y=70, color='red', linestyle='--', linewidth=1, alpha=0.5, label='Overbought (70)')
    ax3.axhline(y=30, color='green', linestyle='--', linewidth=1, alpha=0.5, label='Oversold (30)')
    ax3.fill_between(range(len(plot_data)), 0, 50, alpha=0.1, color='green', label='Buy Zone (RSI < 50)')
    ax3.fill_between(range(len(plot_data)), 50, 100, alpha=0.1, color='red', label='Sell Zone (RSI > 50)')
    
    # Mark RSI at entry points
    if not trades_df.empty:
        for idx, trade in entry_trades.iterrows():
            if idx in plot_data.index:
                rsi_idx = plot_data.index.get_loc(idx)
                rsi_value = trade.get('rsi', plot_data.iloc[rsi_idx]['rsi'])
                ax3.scatter(rsi_idx, rsi_value, color='blue', marker='o',
                           s=100, zorder=5, edgecolors='black', linewidths=1,
                           alpha=0.8)
    
    ax3.set_ylabel('RSI', fontsize=12)
    ax3.set_ylim(0, 100)
    ax3.grid(True, alpha=0.3, linestyle='--')
    ax3.legend(loc='upper right', fontsize=8)
    ax3.set_xticks(tick_positions)
    ax3.set_xticklabels(tick_labels, rotation=45, ha='right')
    
    # Equity curve
    ax4 = fig.add_subplot(gs[3], sharex=ax1)
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
                ax4.plot(equity_indices, equity_values, color='blue', linewidth=2, label='Equity')
                ax4.axhline(y=backtest_data['initial_capital'], color='gray', 
                           linestyle='--', linewidth=1, alpha=0.7, label='Initial Capital')
                ax4.set_ylabel('Equity (USD)', fontsize=12)
                ax4.grid(True, alpha=0.3, linestyle='--')
                ax4.legend(loc='upper left')
    
    ax4.set_xticks(tick_positions)
    ax4.set_xticklabels(tick_labels, rotation=45, ha='right')
    
    # Position size
    ax5 = fig.add_subplot(gs[4], sharex=ax1)
    if not equity_history.empty:
        plot_equity = equity_history[(equity_history.index >= plot_start) & 
                                     (equity_history.index <= plot_end)]
        if not plot_equity.empty and 'position_btc' in plot_equity.columns:
            position_indices = [plot_data.index.get_loc(idx) for idx in plot_equity.index 
                              if idx in plot_data.index]
            position_values = [plot_equity.loc[idx, 'position_btc'] for idx in plot_equity.index 
                             if idx in plot_data.index]
            
            if position_indices:
                # Use different colors for long (positive) and short (negative) positions
                long_positions = [v if v > 0 else 0 for v in position_values]
                short_positions = [abs(v) if v < 0 else 0 for v in position_values]
                
                if any(long_positions):
                    ax5.fill_between(position_indices, 0, long_positions, 
                                    color='green', alpha=0.5, label='Long Position')
                if any(short_positions):
                    ax5.fill_between(position_indices, 0, [-v for v in short_positions], 
                                    color='red', alpha=0.5, label='Short Position')
                ax5.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
                ax5.set_ylabel('Position (BTC)', fontsize=12)
                ax5.grid(True, alpha=0.3, linestyle='--')
                ax5.legend(loc='upper left')
    
    ax5.set_xlabel('Time', fontsize=12)
    ax5.set_xticks(tick_positions)
    ax5.set_xticklabels(tick_labels, rotation=45, ha='right')
    
    plt.tight_layout()
    plt.show()


def plot_trade_analysis(results):
    """
    Plot trade analysis including profit/loss distribution and cumulative returns.
    
    Parameters:
    -----------
    results : dict or Results object
        Backtest results from run_volume_backtest() or Results object
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
    
    # Get exit trades (completed trades)
    exits = trades_df[
        (trades_df['exit_reason'].notna()) & 
        (trades_df['profit_loss'].notna())
    ]
    
    if exits.empty:
        print("No completed trades to analyze.")
        return
    
    # 1. Profit/Loss Distribution
    ax1 = axes[0, 0]
    profit_loss = exits['profit_loss'].dropna()
    if len(profit_loss) > 0:
        ax1.hist(profit_loss, bins=20, color='steelblue', edgecolor='black', alpha=0.7)
        ax1.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Break Even')
        ax1.axvline(x=profit_loss.mean(), color='green', linestyle='--', 
                   linewidth=2, label=f'Mean: ${profit_loss.mean():.2f}')
        ax1.set_xlabel('Profit/Loss (USD)', fontsize=12)
        ax1.set_ylabel('Frequency', fontsize=12)
        ax1.set_title('Profit/Loss Distribution', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
    
    # 2. Cumulative Returns
    ax2 = axes[0, 1]
    if not equity_history.empty and 'equity' in equity_history.columns:
        equity = equity_history['equity']
        initial_capital = backtest_data['initial_capital']
        cumulative_returns = ((equity - initial_capital) / initial_capital) * 100
        
        ax2.plot(equity_history.index, cumulative_returns, color='blue', linewidth=2, label='Cumulative Returns')
        ax2.axhline(y=0, color='gray', linestyle='--', linewidth=1, alpha=0.5)
        ax2.set_xlabel('Time', fontsize=12)
        ax2.set_ylabel('Cumulative Returns (%)', fontsize=12)
        ax2.set_title('Cumulative Returns Over Time', fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # 3. Exit Reason Distribution
    ax3 = axes[1, 0]
    exit_reasons = exits['exit_reason'].value_counts()
    if len(exit_reasons) > 0:
        colors = {'TAKE_PROFIT': 'green', 'STOP_LOSS': 'red', 'MAX_HOLDING': 'orange'}
        bar_colors = [colors.get(reason, 'gray') for reason in exit_reasons.index]
        ax3.bar(exit_reasons.index, exit_reasons.values, color=bar_colors, alpha=0.7, edgecolor='black')
        ax3.set_xlabel('Exit Reason', fontsize=12)
        ax3.set_ylabel('Count', fontsize=12)
        ax3.set_title('Exit Reason Distribution', fontsize=14, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')
    
    # 4. Profit/Loss by Exit Reason
    ax4 = axes[1, 1]
    if 'exit_reason' in exits.columns:
        exit_reason_groups = exits.groupby('exit_reason')['profit_loss']
        exit_reasons_list = exit_reason_groups.groups.keys()
        
        data_to_plot = []
        labels = []
        for reason in exit_reasons_list:
            pnl_values = exit_reason_groups.get_group(reason).values
            if len(pnl_values) > 0:
                data_to_plot.append(pnl_values)
                labels.append(f"{reason}\n(n={len(pnl_values)})")
        
        if data_to_plot:
            bp = ax4.boxplot(data_to_plot, labels=labels, patch_artist=True)
            for patch, reason in zip(bp['boxes'], exit_reasons_list):
                if reason == 'TAKE_PROFIT':
                    patch.set_facecolor('green')
                elif reason == 'STOP_LOSS':
                    patch.set_facecolor('red')
                else:
                    patch.set_facecolor('orange')
                patch.set_alpha(0.7)
            
            ax4.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
            ax4.set_ylabel('Profit/Loss (USD)', fontsize=12)
            ax4.set_title('Profit/Loss by Exit Reason', fontsize=14, fontweight='bold')
            ax4.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.show()
    
    # Print summary statistics
    print("\n" + "=" * 70)
    print("TRADE ANALYSIS SUMMARY")
    print("=" * 70)
    print(f"Total Completed Trades: {len(exits)}")
    winning_trades = exits[exits['profit_loss'] > 0]
    losing_trades = exits[exits['profit_loss'] <= 0]
    print(f"Winning Trades: {len(winning_trades)}")
    print(f"Losing Trades: {len(losing_trades)}")
    if len(exits) > 0:
        print(f"Win Rate: {(len(winning_trades) / len(exits)) * 100:.2f}%")
        print(f"Average Profit/Loss: ${exits['profit_loss'].mean():,.2f}")
        print(f"Best Trade: ${exits['profit_loss'].max():,.2f}")
        print(f"Worst Trade: ${exits['profit_loss'].min():,.2f}")
        print(f"Total Profit/Loss: ${exits['profit_loss'].sum():,.2f}")
    print("=" * 70)
