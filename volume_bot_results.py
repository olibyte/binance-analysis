"""
Volume Breakout Trading Bot Results Module

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
        Dictionary returned from run_volume_backtest()
    
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
            
            # Get exit trades (completed trades with profit_loss)
            exits = self.trades_df[
                (self.trades_df['exit_reason'].notna()) & 
                (self.trades_df['profit_loss'].notna())
            ]
            if exits.empty:
                return 0.0
            
            # Trades with profit_loss > 0
            profitable = exits[exits['profit_loss'] > 0]
            return (len(profitable) / len(exits)) * 100 if len(exits) > 0 else 0.0
        
        def _calculate_avg_profit_loss(self):
            """Calculate average profit/loss per trade."""
            if self.trades_df.empty:
                return 0.0
            
            exits = self.trades_df[
                (self.trades_df['exit_reason'].notna()) & 
                (self.trades_df['profit_loss'].notna())
            ]
            if exits.empty:
                return 0.0
            
            return exits['profit_loss'].mean()
        
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
            
            # Assuming 15-minute candles, 96 candles per day (24*4)
            # Annualize based on 15-minute periods
            periods_per_year = 96 * 365
            excess_returns = returns - (risk_free_rate / periods_per_year)
            sharpe = (excess_returns.mean() / returns.std()) * np.sqrt(periods_per_year) if returns.std() > 0 else 0.0
            
            return sharpe
        
        def _calculate_tp_hits(self):
            """Count trades closed at Take Profit."""
            if self.trades_df.empty:
                return 0
            
            exits = self.trades_df[
                (self.trades_df['exit_reason'].notna()) & 
                (self.trades_df['exit_reason'] == 'TAKE_PROFIT')
            ]
            return len(exits)
        
        def _calculate_sl_hits(self):
            """Count trades closed at Stop Loss."""
            if self.trades_df.empty:
                return 0
            
            exits = self.trades_df[
                (self.trades_df['exit_reason'].notna()) & 
                (self.trades_df['exit_reason'] == 'STOP_LOSS')
            ]
            return len(exits)
        
        def _calculate_max_holding_hits(self):
            """Count trades closed at Max Holding Period."""
            if self.trades_df.empty:
                return 0
            
            exits = self.trades_df[
                (self.trades_df['exit_reason'].notna()) & 
                (self.trades_df['exit_reason'] == 'MAX_HOLDING')
            ]
            return len(exits)
        
        def _calculate_tp_sl_ratio(self):
            """Calculate TP:SL ratio."""
            tp_hits = self._calculate_tp_hits()
            sl_hits = self._calculate_sl_hits()
            
            if sl_hits == 0:
                return float('inf') if tp_hits > 0 else 0.0
            
            return tp_hits / sl_hits
        
        def get_metrics(self):
            """Get all metrics as a dictionary."""
            drawdown = self._calculate_max_drawdown()
            
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
                'max_holding_hits': self._calculate_max_holding_hits(),
                'tp_sl_ratio': self._calculate_tp_sl_ratio()
            }
            
            return metrics
        
        def print_summary(self):
            """Print formatted summary of backtest results."""
            metrics = self.get_metrics()
            config = self.data.get('config', {})
            
            print("=" * 70)
            print("VOLUME BREAKOUT TRADING BOT BACKTEST REPORT")
            print("=" * 70)
            print()
            
            # Configuration
            print("CONFIGURATION:")
            print(f"  Initial Capital: ${metrics['initial_capital']:,.2f}")
            print(f"  Volume Threshold: {config.get('volume_threshold_btc', 1.0):.2f} BTC")
            print(f"  Risk: {config.get('risk_pct', 1.0):.2f}%")
            print(f"  Reward: {config.get('reward_pct', 2.0):.2f}%")
            print(f"  Risk:Reward Ratio: 1:{config.get('reward_pct', 2.0) / config.get('risk_pct', 1.0):.1f}")
            print(f"  Max Holding Period: {config.get('max_holding_candles', 5)} candles")
            print(f"  RSI Period: {config.get('rsi_period', 14)}")
            print(f"  RSI Buy Filter: < 50")
            print(f"  RSI Sell Filter: > 50")
            print(f"  Trading Fee: {config.get('fee_pct', 0.001) * 100:.2f}%")
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
            
            # Get completed trades
            exits = self.trades_df[
                (self.trades_df['exit_reason'].notna()) & 
                (self.trades_df['profit_loss'].notna())
            ]
            if not exits.empty:
                print(f"  Completed Trades: {len(exits)}")
                print(f"  Win Rate: {metrics['win_rate']:.2f}%")
                print(f"  Avg Profit/Loss per Trade: ${metrics['avg_profit_loss']:,.2f}")
                
                # Best and worst trades
                best_trade = exits['profit_loss'].max()
                worst_trade = exits['profit_loss'].min()
                print(f"  Best Trade: ${best_trade:,.2f}")
                print(f"  Worst Trade: ${worst_trade:,.2f}")
            
            # Exit Reason Statistics
            if not exits.empty:
                print()
                print("EXIT REASON STATISTICS:")
                print(f"  Take Profit: {metrics['tp_hits']}")
                print(f"  Stop Loss: {metrics['sl_hits']}")
                print(f"  Max Holding Period: {metrics['max_holding_hits']}")
                if len(exits) > 0:
                    tp_pct = (metrics['tp_hits'] / len(exits)) * 100
                    sl_pct = (metrics['sl_hits'] / len(exits)) * 100
                    max_hold_pct = (metrics['max_holding_hits'] / len(exits)) * 100
                    print(f"  TP: {tp_pct:.1f}% | SL: {sl_pct:.1f}% | Max Hold: {max_hold_pct:.1f}%")
                if metrics['sl_hits'] > 0:
                    print(f"  TP:SL Ratio: {metrics['tp_sl_ratio']:.2f}")
                elif metrics['tp_hits'] > 0:
                    print(f"  TP:SL Ratio: ∞ (no stop losses hit)")
            print()
            
            # Risk Metrics
            print("RISK METRICS:")
            print(f"  Max Drawdown: ${metrics['max_drawdown']:,.2f} ({metrics['max_drawdown_pct']:.2f}%)")
            print(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
            print(f"  Total Fees Paid: ${metrics['total_fees']:,.2f}")
            print()
            
            # Final Position
            if self.data['final_position_btc'] != 0:
                print("FINAL POSITION:")
                print(f"  BTC Position: {self.data['final_position_btc']:.8f}")
                print(f"  Position Value: ${self.data['final_position_value']:,.2f}")
                print(f"  Cash: ${self.data['final_cash']:,.2f}")
                print()
            
            print("=" * 70)
        
        def export_all(self, prefix="volume_bot_backtest"):
            """
            Export all results to CSV files.
            
            Parameters:
            -----------
            prefix : str
                Prefix for output filenames (default: "volume_bot_backtest")
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
