"""
Volume Breakout Trading Bot Backtest Module

This module implements a volume-based momentum/breakout trading bot that backtests over historical data.
Strategy: Monitor for silence, then ride breakout on volume.

Trading rules:
- Monitor 15m candles
- If volume > n BTC and candle is bullish (close > open) and RSI < 50: 
  Place buy stop above HIGH of breakout candle (to catch upward momentum continuation)
- If volume > n BTC and candle is bearish (close < open) and RSI > 50: 
  Place sell stop below LOW of breakout candle (to catch downward momentum continuation)
- Risk: 1%, Reward: 2% (2:1 R:R)
- Maximum holding period: 5 candles

Direction Logic:
- Bullish breakout candle → Buy stop above high → Enter LONG when price breaks above breakout high
- Bearish breakout candle → Sell stop below low → Enter SHORT when price breaks below breakout low
"""

import pandas as pd
import numpy as np
from calculations import calculate_rsi


def run_volume_backtest(df, initial_capital=10000, volume_threshold_btc=1.0, 
                       risk_pct=1.0, reward_pct=2.0, max_holding_candles=5,
                       rsi_period=14, fee_pct=0.001, stop_order_buffer_pct=0.001):
    """
    Run volume breakout trading bot backtest over historical data.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data (must have 'open', 'high', 'low', 'close', 'volume' columns)
    initial_capital : float
        Starting capital in USD (default: 10000)
    volume_threshold_btc : float
        Volume threshold in BTC (default: 1.0)
    risk_pct : float
        Risk percentage from entry price (default: 1.0)
    reward_pct : float
        Reward percentage from entry price (default: 2.0)
    max_holding_candles : int
        Maximum number of candles to hold a position (default: 5)
    rsi_period : int
        RSI calculation period (default: 14)
    fee_pct : float
        Trading fee percentage (default: 0.001 = 0.1%)
    stop_order_buffer_pct : float
        Small buffer above/below close for stop orders (default: 0.001 = 0.1%)
    
    Returns:
    --------
    dict
        Dictionary containing backtest results with keys:
        - initial_capital: Starting capital
        - final_cash: Final cash balance
        - final_position_btc: Final BTC position
        - final_equity: Final total equity
        - trades: List of trade dictionaries
        - equity_history: DataFrame with equity over time
        - trades_df: DataFrame of all trades
    """
    # Calculate RSI
    df = calculate_rsi(df.copy(), period=rsi_period)
    
    # Initialize state
    cash = initial_capital
    position_btc = 0.0
    position_entry_price = 0.0
    position_entry_candle_idx = None
    position_stop_loss = 0.0
    position_take_profit = 0.0
    position_candles_held = 0
    position_type = None  # 'LONG' or 'SHORT'
    
    # Pending stop orders
    pending_stop_orders = []  # List of {'type': 'BUY_STOP'/'SELL_STOP', 'trigger_price': float, 'signal_candle': timestamp, 'rsi': float}
    
    trades = []
    equity_history = []
    
    # Iterate through each candle
    for idx, row in df.iterrows():
        current_price = row['close']
        high_price = row['high']
        low_price = row['low']
        volume = row['volume']
        rsi = row.get('rsi', np.nan)
        
        # Skip if RSI is NaN (not enough data)
        if pd.isna(rsi):
            # Still track equity
            current_equity = cash + (position_btc * current_price)
            equity_history.append({
                'timestamp': idx,
                'cash': cash,
                'position_btc': position_btc,
                'price': current_price,
                'equity': current_equity
            })
            continue
        
        # Check if we have a position open
        has_position = position_btc != 0.0
        
        # First, check for volume breakout signals and place stop orders
        if not has_position:
            # Check for buy stop signal: volume > threshold + bullish candle + RSI < 50
            # For momentum/breakout: bullish candle means price moved up, place buy stop above HIGH to catch continuation
            is_bullish = row['close'] > row['open']
            if volume > volume_threshold_btc and is_bullish and rsi < 50:
                # Place buy stop order above HIGH of breakout candle (true breakout entry)
                trigger_price = row['high'] * (1 + stop_order_buffer_pct)
                pending_stop_orders.append({
                    'type': 'BUY_STOP',
                    'trigger_price': trigger_price,
                    'signal_candle': idx,
                    'rsi': rsi,
                    'volume': volume,
                    'breakout_high': row['high'],
                    'breakout_low': row['low']
                })
            
            # Check for sell stop signal: volume > threshold + bearish candle + RSI > 50
            # For momentum/breakout: bearish candle means price moved down, place sell stop below LOW to catch continuation
            is_bearish = row['close'] < row['open']
            if volume > volume_threshold_btc and is_bearish and rsi > 50:
                # Place sell stop order below LOW of breakout candle (true breakout entry)
                trigger_price = row['low'] * (1 - stop_order_buffer_pct)
                pending_stop_orders.append({
                    'type': 'SELL_STOP',
                    'trigger_price': trigger_price,
                    'signal_candle': idx,
                    'rsi': rsi,
                    'volume': volume,
                    'breakout_high': row['high'],
                    'breakout_low': row['low']
                })
        
        # Check if any pending stop orders trigger
        triggered_orders = []
        for order in pending_stop_orders:
            if order['type'] == 'BUY_STOP':
                # Buy stop triggers if price crosses above trigger (high >= trigger)
                if high_price >= order['trigger_price']:
                    triggered_orders.append(order)
            elif order['type'] == 'SELL_STOP':
                # Sell stop triggers if price crosses below trigger (low <= trigger)
                if low_price <= order['trigger_price']:
                    triggered_orders.append(order)
        
        # Execute triggered orders (only one position at a time)
        for order in triggered_orders:
            if not has_position:  # Only enter if no position
                entry_price = order['trigger_price']  # Enter at stop order trigger price
                
                if order['type'] == 'BUY_STOP':
                    # Enter long position
                    # Calculate position size based on risk
                    risk_amount = cash * (risk_pct / 100)
                    stop_loss_price = entry_price * (1 - risk_pct / 100)
                    take_profit_price = entry_price * (1 + reward_pct / 100)
                    
                    # Calculate BTC amount based on risk
                    price_distance_to_sl = entry_price - stop_loss_price
                    btc_amount = risk_amount / price_distance_to_sl
                    
                    # Apply fee on entry
                    fee = btc_amount * fee_pct
                    btc_amount_after_fee = btc_amount - fee
                    
                    # Calculate cost
                    cost = btc_amount * entry_price
                    
                    # Update state
                    cash -= cost
                    position_btc = btc_amount_after_fee
                    position_entry_price = entry_price
                    position_entry_candle_idx = idx
                    position_stop_loss = stop_loss_price
                    position_take_profit = take_profit_price
                    position_candles_held = 0
                    position_type = 'LONG'
                    has_position = True
                    
                    # Record trade
                    trade_record = {
                        'timestamp': idx,
                        'type': 'BUY',
                        'price': entry_price,
                        'amount_usd': cost,
                        'amount_btc': btc_amount_after_fee,
                        'fee_btc': fee,
                        'fee_usd': fee * entry_price,
                        'rsi': order['rsi'],
                        'signal_type': 'VOLUME_BREAKOUT',
                        'volume': order['volume'],
                        'stop_loss': stop_loss_price,
                        'take_profit': take_profit_price,
                        'cash_after': cash,
                        'position_btc_after': position_btc
                    }
                    trades.append(trade_record)
                
                elif order['type'] == 'SELL_STOP':
                    # Enter short position (sell first, buy back later)
                    # Calculate position size based on risk
                    risk_amount = cash * (risk_pct / 100)
                    stop_loss_price = entry_price * (1 + risk_pct / 100)  # For short, SL is above entry
                    take_profit_price = entry_price * (1 - reward_pct / 100)  # For short, TP is below entry
                    
                    # Calculate BTC amount based on risk
                    price_distance_to_sl = stop_loss_price - entry_price
                    btc_amount = risk_amount / price_distance_to_sl
                    
                    # Apply fee on entry (selling)
                    fee = btc_amount * fee_pct
                    btc_amount_after_fee = btc_amount - fee
                    
                    # Calculate proceeds from sale
                    proceeds = btc_amount_after_fee * entry_price
                    
                    # Update state (negative BTC for short position)
                    cash += proceeds
                    position_btc = -btc_amount_after_fee  # Negative for short
                    position_entry_price = entry_price
                    position_entry_candle_idx = idx
                    position_stop_loss = stop_loss_price
                    position_take_profit = take_profit_price
                    position_candles_held = 0
                    position_type = 'SHORT'
                    has_position = True
                    
                    # Record trade
                    trade_record = {
                        'timestamp': idx,
                        'type': 'SELL',
                        'price': entry_price,
                        'amount_usd': proceeds,
                        'amount_btc': btc_amount_after_fee,
                        'fee_btc': fee,
                        'fee_usd': fee * entry_price,
                        'rsi': order['rsi'],
                        'signal_type': 'VOLUME_BREAKOUT',
                        'volume': order['volume'],
                        'stop_loss': stop_loss_price,
                        'take_profit': take_profit_price,
                        'cash_after': cash,
                        'position_btc_after': position_btc
                    }
                    trades.append(trade_record)
        
        # Remove triggered orders from pending list
        for order in triggered_orders:
            if order in pending_stop_orders:
                pending_stop_orders.remove(order)
        
        # Manage open position
        if has_position:
            position_candles_held += 1
            
            # Check exit conditions in priority order
            exit_reason = None
            exit_price = current_price
            
            if position_type == 'LONG':
                # Check Take Profit (price >= TP)
                if high_price >= position_take_profit:
                    exit_price = position_take_profit
                    exit_reason = 'TAKE_PROFIT'
                # Check Stop Loss (price <= SL)
                elif low_price <= position_stop_loss:
                    exit_price = position_stop_loss
                    exit_reason = 'STOP_LOSS'
                # Check Max Holding Period
                elif position_candles_held >= max_holding_candles:
                    exit_reason = 'MAX_HOLDING'
            
            elif position_type == 'SHORT':
                # Check Take Profit (price <= TP, for short TP is below entry)
                if low_price <= position_take_profit:
                    exit_price = position_take_profit
                    exit_reason = 'TAKE_PROFIT'
                # Check Stop Loss (price >= SL, for short SL is above entry)
                elif high_price >= position_stop_loss:
                    exit_price = position_stop_loss
                    exit_reason = 'STOP_LOSS'
                # Check Max Holding Period
                elif position_candles_held >= max_holding_candles:
                    exit_reason = 'MAX_HOLDING'
            
            # Close position if exit condition met
            if exit_reason:
                if position_type == 'LONG':
                    # Close long position (sell)
                    position_value = position_btc * exit_price
                    fee = position_btc * fee_pct
                    btc_to_sell_after_fee = position_btc - fee
                    usd_received = btc_to_sell_after_fee * exit_price
                    
                    # Calculate profit/loss
                    profit_loss = (exit_price - position_entry_price) * btc_to_sell_after_fee - (fee * exit_price)
                    
                    # Record trade
                    trade_record = {
                        'timestamp': idx,
                        'type': 'SELL',
                        'price': exit_price,
                        'amount_usd': usd_received,
                        'amount_btc': btc_to_sell_after_fee,
                        'fee_btc': fee,
                        'fee_usd': fee * exit_price,
                        'rsi': rsi,
                        'signal_type': exit_reason,
                        'exit_reason': exit_reason,
                        'volume': volume,
                        'cash_after': cash + usd_received,
                        'position_btc_after': 0.0,
                        'profit_loss': profit_loss,
                        'candles_held': position_candles_held
                    }
                    trades.append(trade_record)
                    
                    # Update state
                    cash += usd_received
                    position_btc = 0.0
                    position_entry_price = 0.0
                    position_entry_candle_idx = None
                    position_stop_loss = 0.0
                    position_take_profit = 0.0
                    position_candles_held = 0
                    position_type = None
                
                elif position_type == 'SHORT':
                    # Close short position (buy back)
                    # For short, we need to buy back the BTC we sold
                    btc_to_buy = abs(position_btc)  # Make positive
                    cost = btc_to_buy * exit_price
                    fee = btc_to_buy * fee_pct
                    btc_to_buy_after_fee = btc_to_buy + fee  # Add fee to cost
                    total_cost = btc_to_buy_after_fee * exit_price
                    
                    # Calculate profit/loss (for short: profit when price goes down)
                    # We sold at entry_price, buying back at exit_price
                    profit_loss = (position_entry_price - exit_price) * btc_to_buy - (fee * exit_price)
                    
                    # Record trade
                    trade_record = {
                        'timestamp': idx,
                        'type': 'BUY',
                        'price': exit_price,
                        'amount_usd': total_cost,
                        'amount_btc': btc_to_buy_after_fee,
                        'fee_btc': fee,
                        'fee_usd': fee * exit_price,
                        'rsi': rsi,
                        'signal_type': exit_reason,
                        'exit_reason': exit_reason,
                        'volume': volume,
                        'cash_after': cash - total_cost,
                        'position_btc_after': 0.0,
                        'profit_loss': profit_loss,
                        'candles_held': position_candles_held
                    }
                    trades.append(trade_record)
                    
                    # Update state
                    cash -= total_cost
                    position_btc = 0.0
                    position_entry_price = 0.0
                    position_entry_candle_idx = None
                    position_stop_loss = 0.0
                    position_take_profit = 0.0
                    position_candles_held = 0
                    position_type = None
        
        # Track equity at each candle
        if position_btc > 0:
            # Long position: equity = cash + position value
            current_equity = cash + (position_btc * current_price)
        elif position_btc < 0:
            # Short position: equity = cash - (BTC_owed * current_price)
            current_equity = cash - (abs(position_btc) * current_price)
        else:
            # No position
            current_equity = cash
        
        equity_history.append({
            'timestamp': idx,
            'cash': cash,
            'position_btc': position_btc,
            'price': current_price,
            'equity': current_equity,
            'rsi': rsi
        })
    
    # Calculate final equity
    final_price = df.iloc[-1]['close']
    if position_btc > 0:
        final_equity = cash + (position_btc * final_price)
    elif position_btc < 0:
        final_equity = cash - (abs(position_btc) * final_price)
    else:
        final_equity = cash
    
    # Convert equity history to DataFrame
    equity_df = pd.DataFrame(equity_history)
    if not equity_df.empty:
        equity_df.set_index('timestamp', inplace=True)
    
    # Convert trades to DataFrame
    trades_df = pd.DataFrame(trades)
    if not trades_df.empty:
        trades_df.set_index('timestamp', inplace=True)
    
    # Return results
    return {
        'initial_capital': initial_capital,
        'final_cash': cash,
        'final_position_btc': position_btc,
        'final_position_value': abs(position_btc) * final_price if position_btc != 0 else 0,
        'final_equity': final_equity,
        'total_return': final_equity - initial_capital,
        'total_return_pct': ((final_equity - initial_capital) / initial_capital) * 100,
        'trades': trades,
        'trades_df': trades_df,
        'equity_history': equity_df,
        'num_trades': len(trades),
        'num_buys': len([t for t in trades if t['type'] == 'BUY']),
        'num_sells': len([t for t in trades if t['type'] == 'SELL']),
        'total_fees': sum(t.get('fee_usd', 0) for t in trades),
        'config': {
            'volume_threshold_btc': volume_threshold_btc,
            'risk_pct': risk_pct,
            'reward_pct': reward_pct,
            'max_holding_candles': max_holding_candles,
            'rsi_period': rsi_period,
            'fee_pct': fee_pct,
            'stop_order_buffer_pct': stop_order_buffer_pct
        }
    }
