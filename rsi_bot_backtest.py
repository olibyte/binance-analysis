"""
RSI Trading Bot Backtest Module

This module implements a simple RSI-based trading bot that backtests over historical data.
Trading rules:
- Buy when RSI < 30 OR bullish divergence (buy $1000 worth)
- Sell when RSI > 70 OR bearish divergence (sell $1000 worth or entire position if smaller)
- Max 1 position open at a time
- Trading fees: 0.1% per trade
- Divergence can trigger trades even when RSI is not at extreme levels
"""

import pandas as pd
import numpy as np
from calculations import calculate_rsi, detect_rsi_divergence, calculate_volume_indicators, check_volume_participation


def run_rsi_backtest(df, initial_capital=10000, buy_amount=1000, sell_amount=1000, 
                     rsi_period=14, fee_pct=0.001, rsi_buy_threshold=30, rsi_sell_threshold=70,
                     use_divergence=True, divergence_lookback=20, take_profit_pct=1.25, stop_loss_pct=0.75,
                     use_volume_participation=False, volume_participation_required=False,
                     vol_fast_period=20, vol_slow_period=50, volume_spike_threshold=1.5):
    """
    Run RSI trading bot backtest over historical data.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with OHLC data (must have 'close' column)
    initial_capital : float
        Starting capital in USD (default: 10000)
    buy_amount : float
        Amount in USD to buy when RSI < threshold (default: 1000)
    sell_amount : float
        Amount in USD to sell when RSI > threshold (default: 1000)
    rsi_period : int
        RSI calculation period (default: 14)
    fee_pct : float
        Trading fee percentage (default: 0.001 = 0.1%)
    rsi_buy_threshold : float
        RSI threshold for buy signal (default: 30)
    rsi_sell_threshold : float
        RSI threshold for sell signal (default: 70)
    use_divergence : bool
        Enable divergence detection as confluence (default: True)
    divergence_lookback : int
        Lookback period for divergence detection (default: 20)
    take_profit_pct : float
        Take profit percentage from entry price (default: 5.0)
    stop_loss_pct : float
        Stop loss percentage from entry price (default: 3.0)
    use_volume_participation : bool
        Enable volume participation as confluence filter (default: False)
    volume_participation_required : bool
        If True, only take trades with volume confirmation (default: False)
    vol_fast_period : int
        Fast volume MA period (default: 20)
    vol_slow_period : int
        Slow volume MA period (default: 50)
    volume_spike_threshold : float
        Multiplier for volume spike detection (default: 1.5)
    
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
    
    # Calculate volume indicators if volume participation is enabled
    if use_volume_participation:
        df = calculate_volume_indicators(df, fast_period=vol_fast_period, slow_period=vol_slow_period)
    
    # Detect RSI divergence if enabled
    if use_divergence:
        df = detect_rsi_divergence(df, lookback=divergence_lookback)
    else:
        # Initialize divergence columns as False if not using divergence
        df['bearish_divergence'] = False
        df['bullish_divergence'] = False
    
    # Initialize state
    cash = initial_capital
    position_btc = 0.0
    position_entry_price = 0.0
    trades = []
    equity_history = []
    
    # Iterate through each candle
    for idx, row in df.iterrows():
        # Get integer position for volume participation check
        idx_pos = df.index.get_loc(idx)
        current_price = row['close']
        rsi = row['rsi']
        
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
        has_position = position_btc > 0
        
        # Trading logic
        if not has_position:
            # No position open - check for buy signal
            # Buy signal: RSI < threshold OR bullish divergence
            bullish_div = row.get('bullish_divergence', False) if use_divergence else False
            buy_signal = (rsi < rsi_buy_threshold) or bullish_div
            
            # Check volume participation if enabled
            volume_confirmed = True
            volume_participation_details = {}
            if use_volume_participation and buy_signal:
                vol_participation = check_volume_participation(
                    df, idx_pos, 'buy', 
                    vol_fast_period=vol_fast_period, 
                    vol_slow_period=vol_slow_period,
                    spike_threshold=volume_spike_threshold
                )
                volume_confirmed = vol_participation['confirmed']
                volume_participation_details = vol_participation
                
                # If volume participation is required, skip trade if not confirmed
                if volume_participation_required and not volume_confirmed:
                    buy_signal = False
            
            if buy_signal:
                # Determine signal type
                if bullish_div and rsi >= rsi_buy_threshold:
                    signal_type = 'DIVERGENCE'
                elif rsi < rsi_buy_threshold and not bullish_div:
                    signal_type = 'RSI_THRESHOLD'
                else:
                    # Both conditions met, prefer divergence as it's more specific
                    signal_type = 'DIVERGENCE' if bullish_div else 'RSI_THRESHOLD'
                
                # Execute buy
                if cash >= buy_amount:
                    # Calculate BTC amount to buy
                    btc_amount = buy_amount / current_price
                    fee = btc_amount * fee_pct
                    btc_amount_after_fee = btc_amount - fee
                    
                    # Update state
                    cash -= buy_amount
                    position_btc = btc_amount_after_fee
                    position_entry_price = current_price
                    
                    # Record trade
                    trade_record = {
                        'timestamp': idx,
                        'type': 'BUY',
                        'price': current_price,
                        'amount_usd': buy_amount,
                        'amount_btc': btc_amount_after_fee,
                        'fee_btc': fee,
                        'fee_usd': fee * current_price,
                        'rsi': rsi,
                        'signal_type': signal_type,
                        'bullish_divergence': bullish_div,
                        'cash_after': cash,
                        'position_btc_after': position_btc
                    }
                    
                    # Add volume participation details if enabled
                    if use_volume_participation:
                        trade_record['volume_participation'] = volume_confirmed
                        trade_record['volume_conviction'] = volume_participation_details.get('conviction', 'none')
                        trade_record['volume_reason'] = volume_participation_details.get('reason', '')
                        trade_record['volume_spike'] = volume_participation_details.get('volume_spike', False)
                    else:
                        trade_record['volume_participation'] = None
                        trade_record['volume_conviction'] = None
                        trade_record['volume_reason'] = None
                        trade_record['volume_spike'] = None
                    
                    trades.append(trade_record)
        
        else:
            # Position open - check TP/SL first, then RSI signals
            current_pnl_pct = ((current_price - position_entry_price) / position_entry_price) * 100
            
            # Check Take Profit
            if current_pnl_pct >= take_profit_pct:
                # Close position at TP
                exit_reason = 'TAKE_PROFIT'
                
                # Calculate current position value
                position_value = position_btc * current_price
                
                # Sell entire position
                fee = position_btc * fee_pct
                btc_to_sell_after_fee = position_btc - fee
                usd_received = btc_to_sell_after_fee * current_price
                
                # Calculate profit/loss
                profit_loss = (current_price - position_entry_price) * btc_to_sell_after_fee - (fee * current_price)
                
                # Record trade
                trade_record = {
                    'timestamp': idx,
                    'type': 'SELL',
                    'price': current_price,
                    'amount_usd': usd_received,
                    'amount_btc': btc_to_sell_after_fee,
                    'fee_btc': fee,
                    'fee_usd': fee * current_price,
                    'rsi': rsi,
                    'signal_type': exit_reason,
                    'exit_reason': exit_reason,
                    'bearish_divergence': False,
                    'cash_after': cash + usd_received,
                    'position_btc_after': 0.0,
                    'profit_loss': profit_loss
                }
                
                # Add volume participation details (TP/SL exits don't check volume)
                trade_record['volume_participation'] = None
                trade_record['volume_conviction'] = None
                trade_record['volume_reason'] = None
                trade_record['volume_spike'] = None
                
                trades.append(trade_record)
                
                # Update state
                cash += usd_received
                position_btc = 0.0
                position_entry_price = 0.0
            
            # Check Stop Loss
            elif current_pnl_pct <= -stop_loss_pct:
                # Close position at SL
                exit_reason = 'STOP_LOSS'
                
                # Calculate current position value
                position_value = position_btc * current_price
                
                # Sell entire position
                fee = position_btc * fee_pct
                btc_to_sell_after_fee = position_btc - fee
                usd_received = btc_to_sell_after_fee * current_price
                
                # Calculate profit/loss
                profit_loss = (current_price - position_entry_price) * btc_to_sell_after_fee - (fee * current_price)
                
                # Record trade
                trade_record = {
                    'timestamp': idx,
                    'type': 'SELL',
                    'price': current_price,
                    'amount_usd': usd_received,
                    'amount_btc': btc_to_sell_after_fee,
                    'fee_btc': fee,
                    'fee_usd': fee * current_price,
                    'rsi': rsi,
                    'signal_type': exit_reason,
                    'exit_reason': exit_reason,
                    'bearish_divergence': False,
                    'cash_after': cash + usd_received,
                    'position_btc_after': 0.0,
                    'profit_loss': profit_loss
                }
                
                # Add volume participation details (TP/SL exits don't check volume)
                trade_record['volume_participation'] = None
                trade_record['volume_conviction'] = None
                trade_record['volume_reason'] = None
                trade_record['volume_spike'] = None
                
                trades.append(trade_record)
                
                # Update state
                cash += usd_received
                position_btc = 0.0
                position_entry_price = 0.0
            
            else:
                # No TP/SL hit - check RSI/divergence signals
                # Sell signal: RSI > threshold OR bearish divergence
                bearish_div = row.get('bearish_divergence', False) if use_divergence else False
                sell_signal = (rsi > rsi_sell_threshold) or bearish_div
                
                # Check volume participation if enabled
                volume_confirmed = True
                volume_participation_details = {}
                if use_volume_participation and sell_signal:
                    vol_participation = check_volume_participation(
                        df, idx_pos, 'sell',
                        vol_fast_period=vol_fast_period,
                        vol_slow_period=vol_slow_period,
                        spike_threshold=volume_spike_threshold
                    )
                    volume_confirmed = vol_participation['confirmed']
                    volume_participation_details = vol_participation
                    
                    # If volume participation is required, skip trade if not confirmed
                    if volume_participation_required and not volume_confirmed:
                        sell_signal = False
                
                if sell_signal:
                    # Determine signal type
                    if bearish_div and rsi <= rsi_sell_threshold:
                        signal_type = 'DIVERGENCE'
                        exit_reason = 'DIVERGENCE'
                    elif rsi > rsi_sell_threshold and not bearish_div:
                        signal_type = 'RSI_THRESHOLD'
                        exit_reason = 'RSI_THRESHOLD'
                    else:
                        # Both conditions met, prefer divergence as it's more specific
                        signal_type = 'DIVERGENCE' if bearish_div else 'RSI_THRESHOLD'
                        exit_reason = signal_type
                    
                    # Calculate current position value
                    position_value = position_btc * current_price
                    
                    # Determine sell amount
                    if position_value >= sell_amount:
                        # Sell $sell_amount worth
                        btc_to_sell = sell_amount / current_price
                        # Ensure we don't sell more than we have
                        btc_to_sell = min(btc_to_sell, position_btc)
                        fee = btc_to_sell * fee_pct
                        btc_to_sell_after_fee = btc_to_sell - fee
                        usd_received = (btc_to_sell_after_fee * current_price)
                        
                        # Update state
                        position_btc -= btc_to_sell_after_fee
                        cash += usd_received
                        
                        # If position is very small, close it completely
                        if position_btc < 0.0001:  # Threshold to avoid floating point issues
                            position_btc = 0.0
                            position_entry_price = 0.0
                        
                        # Record trade
                        trade_record = {
                            'timestamp': idx,
                            'type': 'SELL',
                            'price': current_price,
                            'amount_usd': usd_received,
                            'amount_btc': btc_to_sell_after_fee,
                            'fee_btc': fee,
                            'fee_usd': fee * current_price,
                            'rsi': rsi,
                            'signal_type': signal_type,
                            'exit_reason': exit_reason,
                            'bearish_divergence': bearish_div,
                            'cash_after': cash,
                            'position_btc_after': position_btc,
                            'profit_loss': (current_price - position_entry_price) * btc_to_sell_after_fee - (fee * current_price)
                        }
                        
                        # Add volume participation details if enabled
                        if use_volume_participation:
                            trade_record['volume_participation'] = volume_confirmed
                            trade_record['volume_conviction'] = volume_participation_details.get('conviction', 'none')
                            trade_record['volume_reason'] = volume_participation_details.get('reason', '')
                            trade_record['volume_spike'] = volume_participation_details.get('volume_spike', False)
                        else:
                            trade_record['volume_participation'] = None
                            trade_record['volume_conviction'] = None
                            trade_record['volume_reason'] = None
                            trade_record['volume_spike'] = None
                        
                        trades.append(trade_record)
                    else:
                        # Sell entire position (less than $sell_amount)
                        fee = position_btc * fee_pct
                        btc_to_sell_after_fee = position_btc - fee
                        usd_received = btc_to_sell_after_fee * current_price
                        
                        # Calculate profit/loss
                        profit_loss = (current_price - position_entry_price) * btc_to_sell_after_fee - (fee * current_price)
                        
                        # Record trade
                        trade_record = {
                            'timestamp': idx,
                            'type': 'SELL',
                            'price': current_price,
                            'amount_usd': usd_received,
                            'amount_btc': btc_to_sell_after_fee,
                            'fee_btc': fee,
                            'fee_usd': fee * current_price,
                            'rsi': rsi,
                            'signal_type': signal_type,
                            'exit_reason': exit_reason,
                            'bearish_divergence': bearish_div,
                            'cash_after': cash + usd_received,
                            'position_btc_after': 0.0,
                            'profit_loss': profit_loss
                        }
                        
                        # Add volume participation details if enabled
                        if use_volume_participation:
                            trade_record['volume_participation'] = volume_confirmed
                            trade_record['volume_conviction'] = volume_participation_details.get('conviction', 'none')
                            trade_record['volume_reason'] = volume_participation_details.get('reason', '')
                            trade_record['volume_spike'] = volume_participation_details.get('volume_spike', False)
                        else:
                            trade_record['volume_participation'] = None
                            trade_record['volume_conviction'] = None
                            trade_record['volume_reason'] = None
                            trade_record['volume_spike'] = None
                        
                        trades.append(trade_record)
                        
                        # Update state
                        cash += usd_received
                        position_btc = 0.0
                        position_entry_price = 0.0
        
        # Track equity at each candle
        current_equity = cash + (position_btc * current_price)
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
    final_equity = cash + (position_btc * final_price)
    
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
        'final_position_value': position_btc * final_price,
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
            'buy_amount': buy_amount,
            'sell_amount': sell_amount,
            'rsi_period': rsi_period,
            'fee_pct': fee_pct,
            'rsi_buy_threshold': rsi_buy_threshold,
            'rsi_sell_threshold': rsi_sell_threshold,
            'use_divergence': use_divergence,
            'divergence_lookback': divergence_lookback,
            'take_profit_pct': take_profit_pct,
            'stop_loss_pct': stop_loss_pct,
            'use_volume_participation': use_volume_participation,
            'volume_participation_required': volume_participation_required,
            'vol_fast_period': vol_fast_period,
            'vol_slow_period': vol_slow_period,
            'volume_spike_threshold': volume_spike_threshold
        }
    }

