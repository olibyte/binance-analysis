"""
RSI Trading Bot Results Module

This module provides utilities for processing and displaying backtest results.
"""

import pandas as pd
import numpy as np


def create_results(backtest_data):
    """
    Create a results object with helper methods for accessing backtest results.
    
    Parameters:
    -----------
    backtest_data : dict
        Dictionary returned from run_rsi_backtest()
    
    Returns:
    --------
    Results object with methods:
    - print_summary(): Print formatted summary
    - export_all(prefix): Export to CSV files
    - get_metrics(): Get dictionary of all metrics
    """
    class Results:
        def __init__(self, data):
            self.data = data
            self.trades_df = data.get('trades_df', pd.DataFrame())
            self.equity_history = data.get('equity_history', pd.DataFrame())
            
        def _calculate_win_rate(self):
            """Calculate win rate from completed trades."""
            if self.trades_df.empty:
                return 0.0
            
            # Get sell trades (completed trades)
            sells = self.trades_df[self.trades_df['type'] == 'SELL']
            if sells.empty:
                return 0.0
            
            # Trades with profit_loss calculated
            profitable = sells[sells['profit_loss'] > 0]
            return (len(profitable) / len(sells)) * 100 if len(sells) > 0 else 0.0
        
        def _calculate_avg_profit_loss(self):
            """Calculate average profit/loss per trade."""
            if self.trades_df.empty:
                return 0.0
            
            sells = self.trades_df[self.trades_df['type'] == 'SELL']
            if sells.empty or 'profit_loss' not in sells.columns:
                return 0.0
            
            return sells['profit_loss'].mean()
        
        def _calculate_max_drawdown(self):
            """Calculate maximum drawdown."""
            if self.equity_history.empty or 'equity' not in self.equity_history.columns:
                return {'max_drawdown': 0.0, 'max_drawdown_pct': 0.0}
            
            equity = self.equity_history['equity']
            peak = equity.expanding().max()
            drawdown = equity - peak
            max_drawdown = drawdown.min()
            max_drawdown_pct = (max_drawdown / peak[drawdown.idxmin()]) * 100 if peak[drawdown.idxmin()] > 0 else 0.0
            
            return {
                'max_drawdown': abs(max_drawdown),
                'max_drawdown_pct': abs(max_drawdown_pct)
            }
        
        def _calculate_sharpe_ratio(self, risk_free_rate=0.0):
            """Calculate Sharpe ratio (annualized)."""
            if self.equity_history.empty or 'equity' not in self.equity_history.columns:
                return 0.0
            
            equity = self.equity_history['equity']
            returns = equity.pct_change().dropna()
            
            if len(returns) == 0 or returns.std() == 0:
                return 0.0
            
            # Assuming daily returns (adjust if needed)
            # For simplicity, we'll use the period returns directly
            excess_returns = returns - (risk_free_rate / 252)  # Assuming 252 trading days
            sharpe = (excess_returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0.0
            
            return sharpe
        
        def _calculate_tp_hits(self):
            """Count trades closed at Take Profit."""
            if self.trades_df.empty:
                return 0
            
            sells = self.trades_df[self.trades_df['type'] == 'SELL']
            if sells.empty or 'exit_reason' not in sells.columns:
                return 0
            
            tp_trades = sells[sells['exit_reason'] == 'TAKE_PROFIT']
            return len(tp_trades)
        
        def _calculate_sl_hits(self):
            """Count trades closed at Stop Loss."""
            if self.trades_df.empty:
                return 0
            
            sells = self.trades_df[self.trades_df['type'] == 'SELL']
            if sells.empty or 'exit_reason' not in sells.columns:
                return 0
            
            sl_trades = sells[sells['exit_reason'] == 'STOP_LOSS']
            return len(sl_trades)
        
        def _calculate_tp_sl_ratio(self):
            """Calculate TP:SL ratio."""
            tp_hits = self._calculate_tp_hits()
            sl_hits = self._calculate_sl_hits()
            
            if sl_hits == 0:
                return float('inf') if tp_hits > 0 else 0.0
            
            return tp_hits / sl_hits
        
        def _calculate_volume_participation_stats(self):
            """Calculate volume participation statistics."""
            if self.trades_df.empty or 'volume_participation' not in self.trades_df.columns:
                return {
                    'total_with_volume': 0,
                    'total_without_volume': 0,
                    'volume_confirmed_win_rate': 0.0,
                    'volume_confirmed_avg_pnl': 0.0,
                    'no_volume_win_rate': 0.0,
                    'no_volume_avg_pnl': 0.0
                }
            
            # Filter trades that have volume participation data (exclude TP/SL exits)
            volume_trades = self.trades_df[self.trades_df['volume_participation'].notna()]
            
            if volume_trades.empty:
                return {
                    'total_with_volume': 0,
                    'total_without_volume': 0,
                    'volume_confirmed_win_rate': 0.0,
                    'volume_confirmed_avg_pnl': 0.0,
                    'no_volume_win_rate': 0.0,
                    'no_volume_avg_pnl': 0.0
                }
            
            # Get sell trades with volume data
            volume_sells = volume_trades[(volume_trades['type'] == 'SELL') & 
                                         (volume_trades['profit_loss'].notna())]
            
            if volume_sells.empty:
                return {
                    'total_with_volume': len(volume_trades[volume_trades['volume_participation'] == True]),
                    'total_without_volume': len(volume_trades[volume_trades['volume_participation'] == False]),
                    'volume_confirmed_win_rate': 0.0,
                    'volume_confirmed_avg_pnl': 0.0,
                    'no_volume_win_rate': 0.0,
                    'no_volume_avg_pnl': 0.0
                }
            
            # Separate by volume participation
            volume_confirmed = volume_sells[volume_sells['volume_participation'] == True]
            volume_not_confirmed = volume_sells[volume_sells['volume_participation'] == False]
            
            # Calculate win rates
            vol_confirmed_wins = len(volume_confirmed[volume_confirmed['profit_loss'] > 0]) if not volume_confirmed.empty else 0
            vol_confirmed_win_rate = (vol_confirmed_wins / len(volume_confirmed) * 100) if len(volume_confirmed) > 0 else 0.0
            
            vol_not_confirmed_wins = len(volume_not_confirmed[volume_not_confirmed['profit_loss'] > 0]) if not volume_not_confirmed.empty else 0
            vol_not_confirmed_win_rate = (vol_not_confirmed_wins / len(volume_not_confirmed) * 100) if len(volume_not_confirmed) > 0 else 0.0
            
            # Calculate average P/L
            vol_confirmed_avg_pnl = volume_confirmed['profit_loss'].mean() if not volume_confirmed.empty else 0.0
            vol_not_confirmed_avg_pnl = volume_not_confirmed['profit_loss'].mean() if not volume_not_confirmed.empty else 0.0
            
            return {
                'total_with_volume': len(volume_trades[volume_trades['volume_participation'] == True]),
                'total_without_volume': len(volume_trades[volume_trades['volume_participation'] == False]),
                'volume_confirmed_win_rate': vol_confirmed_win_rate,
                'volume_confirmed_avg_pnl': vol_confirmed_avg_pnl,
                'no_volume_win_rate': vol_not_confirmed_win_rate,
                'no_volume_avg_pnl': vol_not_confirmed_avg_pnl
            }
        
        def get_metrics(self):
            """Get all metrics as a dictionary."""
            drawdown = self._calculate_max_drawdown()
            volume_stats = self._calculate_volume_participation_stats()
            
            metrics = {
                'initial_capital': self.data['initial_capital'],
                'final_equity': self.data['final_equity'],
                'total_return': self.data['total_return'],
                'total_return_pct': self.data['total_return_pct'],
                'num_trades': self.data['num_trades'],
                'num_buys': self.data['num_buys'],
                'num_sells': self.data['num_sells'],
                'win_rate': self._calculate_win_rate(),
                'avg_profit_loss': self._calculate_avg_profit_loss(),
                'max_drawdown': drawdown['max_drawdown'],
                'max_drawdown_pct': drawdown['max_drawdown_pct'],
                'sharpe_ratio': self._calculate_sharpe_ratio(),
                'total_fees': self.data['total_fees'],
                'tp_hits': self._calculate_tp_hits(),
                'sl_hits': self._calculate_sl_hits(),
                'tp_sl_ratio': self._calculate_tp_sl_ratio()
            }
            
            # Add volume participation metrics
            metrics.update(volume_stats)
            
            return metrics
        
        def print_summary(self):
            """Print formatted summary of backtest results."""
            metrics = self.get_metrics()
            config = self.data.get('config', {})
            
            print("=" * 70)
            print("RSI TRADING BOT BACKTEST REPORT")
            print("=" * 70)
            print()
            
            # Configuration
            print("CONFIGURATION:")
            print(f"  Initial Capital: ${metrics['initial_capital']:,.2f}")
            print(f"  Buy Amount: ${config.get('buy_amount', 1000):,.2f}")
            print(f"  Sell Amount: ${config.get('sell_amount', 1000):,.2f}")
            print(f"  RSI Period: {config.get('rsi_period', 14)}")
            print(f"  RSI Buy Threshold: < {config.get('rsi_buy_threshold', 30)}")
            print(f"  RSI Sell Threshold: > {config.get('rsi_sell_threshold', 70)}")
            print(f"  Trading Fee: {config.get('fee_pct', 0.001) * 100:.2f}%")
            use_divergence = config.get('use_divergence', False)
            if use_divergence:
                print(f"  Divergence Detection: Enabled (lookback: {config.get('divergence_lookback', 20)})")
            else:
                print(f"  Divergence Detection: Disabled")
            use_volume = config.get('use_volume_participation', False)
            if use_volume:
                vol_required = config.get('volume_participation_required', False)
                vol_threshold = config.get('volume_spike_threshold', 1.5)
                print(f"  Volume Participation: Enabled (required: {vol_required}, spike threshold: {vol_threshold}x)")
            else:
                print(f"  Volume Participation: Disabled")
            take_profit_pct = config.get('take_profit_pct', None)
            stop_loss_pct = config.get('stop_loss_pct', None)
            if take_profit_pct is not None and stop_loss_pct is not None:
                print(f"  Take Profit: +{take_profit_pct:.2f}%")
                print(f"  Stop Loss: -{stop_loss_pct:.2f}%")
            print()
            
            # Returns
            print("RETURNS:")
            print(f"  Initial Capital: ${metrics['initial_capital']:,.2f}")
            print(f"  Final Equity: ${metrics['final_equity']:,.2f}")
            print(f"  Total Return: ${metrics['total_return']:,.2f} ({metrics['total_return_pct']:.2f}%)")
            print()
            
            # Trade Statistics
            print("TRADE STATISTICS:")
            print(f"  Total Trades: {metrics['num_trades']}")
            print(f"  Buy Trades: {metrics['num_buys']}")
            print(f"  Sell Trades: {metrics['num_sells']}")
            if metrics['num_sells'] > 0:
                print(f"  Win Rate: {metrics['win_rate']:.2f}%")
                print(f"  Avg Profit/Loss per Trade: ${metrics['avg_profit_loss']:,.2f}")
            
            # Exit Reason Statistics
            if not self.trades_df.empty and 'exit_reason' in self.trades_df.columns:
                sells = self.trades_df[self.trades_df['type'] == 'SELL']
                if not sells.empty:
                    tp_hits = metrics['tp_hits']
                    sl_hits = metrics['sl_hits']
                    rsi_exits = len(sells[sells['exit_reason'] == 'RSI_THRESHOLD'])
                    div_exits = len(sells[sells['exit_reason'] == 'DIVERGENCE'])
                    
                    print()
                    print("EXIT REASON STATISTICS:")
                    print(f"  Take Profit: {tp_hits}")
                    print(f"  Stop Loss: {sl_hits}")
                    print(f"  RSI Threshold: {rsi_exits}")
                    print(f"  Divergence: {div_exits}")
                    if metrics['num_sells'] > 0:
                        tp_pct = (tp_hits / metrics['num_sells']) * 100
                        sl_pct = (sl_hits / metrics['num_sells']) * 100
                        rsi_pct = (rsi_exits / metrics['num_sells']) * 100
                        div_pct = (div_exits / metrics['num_sells']) * 100
                        print(f"  TP: {tp_pct:.1f}% | SL: {sl_pct:.1f}% | RSI: {rsi_pct:.1f}% | Div: {div_pct:.1f}%")
                    if sl_hits > 0:
                        print(f"  TP:SL Ratio: {metrics['tp_sl_ratio']:.2f}")
                    elif tp_hits > 0:
                        print(f"  TP:SL Ratio: ∞ (no stop losses hit)")
            print()
            
            # Risk Metrics
            print("RISK METRICS:")
            print(f"  Max Drawdown: ${metrics['max_drawdown']:,.2f} ({metrics['max_drawdown_pct']:.2f}%)")
            print(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
            print(f"  Total Fees Paid: ${metrics['total_fees']:,.2f}")
            print()
            
            # Volume Participation Statistics
            if config.get('use_volume_participation', False):
                vol_stats = self._calculate_volume_participation_stats()
                if vol_stats['total_with_volume'] > 0 or vol_stats['total_without_volume'] > 0:
                    print("VOLUME PARTICIPATION STATISTICS:")
                    print(f"  Trades with Volume Confirmation: {vol_stats['total_with_volume']}")
                    print(f"  Trades without Volume Confirmation: {vol_stats['total_without_volume']}")
                    if vol_stats['total_with_volume'] > 0:
                        print(f"  Volume Confirmed Win Rate: {vol_stats['volume_confirmed_win_rate']:.2f}%")
                        print(f"  Volume Confirmed Avg P/L: ${vol_stats['volume_confirmed_avg_pnl']:,.2f}")
                    if vol_stats['total_without_volume'] > 0:
                        print(f"  No Volume Win Rate: {vol_stats['no_volume_win_rate']:.2f}%")
                        print(f"  No Volume Avg P/L: ${vol_stats['no_volume_avg_pnl']:,.2f}")
                    print()
            
            # Final Position
            if self.data['final_position_btc'] > 0:
                print("FINAL POSITION:")
                print(f"  BTC Held: {self.data['final_position_btc']:.8f}")
                print(f"  Position Value: ${self.data['final_position_value']:,.2f}")
                print(f"  Cash: ${self.data['final_cash']:,.2f}")
                print()
            
            print("=" * 70)
        
        def export_all(self, prefix="rsi_bot_backtest"):
            """
            Export all results to CSV files.
            
            Parameters:
            -----------
            prefix : str
                Prefix for output filenames (default: "rsi_bot_backtest")
            """
            # Export trades
            if not self.trades_df.empty:
                trades_file = f"{prefix}_trades.csv"
                self.trades_df.to_csv(trades_file)
                print(f"Exported trades to: {trades_file}")
            
            # Export equity history
            if not self.equity_history.empty:
                equity_file = f"{prefix}_equity_history.csv"
                self.equity_history.to_csv(equity_file)
                print(f"Exported equity history to: {equity_file}")
            
            # Export summary metrics
            metrics = self.get_metrics()
            metrics_df = pd.DataFrame([metrics])
            summary_file = f"{prefix}_summary.csv"
            metrics_df.to_csv(summary_file, index=False)
            print(f"Exported summary to: {summary_file}")
    
    return Results(backtest_data)

