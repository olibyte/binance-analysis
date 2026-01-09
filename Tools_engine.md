# Bias Tool - Trading Indicator Scoring Guide

A tool for scoring trading bias using MACD, RSI, and Bollinger Bands indicators. Each indicator is scored as **1** (BUY), **-1** (SELL), or **0** (NEUTRAL).

## Indicator Setup

Configure your charting software (TradingView, MT4, etc.) with these exact parameters:

- **MACD:** Fast Length = 8, Slow Length = 21, Signal Smoothing = 5
- **RSI:** Length = 5 (mark lines at 80 and 20)
- **Bollinger Bands:** Length = 20, Basis = EMA (Exponential Moving Average)

## Scoring Rules

### Column M: MACD (Momentum)

- **1 (BUY):** MACD line above Signal line (Histogram is Green/Positive)
- **-1 (SELL):** MACD line below Signal line (Histogram is Red/Negative)
- **0 (NEUTRAL):** Lines are flat/entwined, no clear momentum

### Column R: RSI (Relative Strength)

**Deep/DD Timeframes (Month, Week, Day, 4hr):** Look for reversals

- **1 (BUY):** RSI < 20 (Oversold)
- **-1 (SELL):** RSI > 80 (Overbought)
- **0 (NEUTRAL):** RSI between 20-80

**Now Timeframes (1hr, 15min, 5min):** Trend filter relative to 50

- **1 (BUY):** RSI > 50
- **-1 (SELL):** RSI < 50
- **0 (NEUTRAL):** RSI exactly at 50

### Column B: Bollinger Bands (Trend/Structure)

- **1 (BUY):** Price closing above 20 EMA (middle line)
- **-1 (SELL):** Price closing below 20 EMA (middle line)
- **0 (NEUTRAL):** Price oscillating across middle line (ranging/choppy)

## Quick Reference Table

| Timeframe             | M (MACD)                              | R (RSI)                                 | B (Bollinger)                           |
| --------------------- | ------------------------------------- | --------------------------------------- | --------------------------------------- |
| **Month/Week/Day/4H** | 1: MACD > Signal<br>-1: MACD < Signal | 1: RSI < 20<br>-1: RSI > 80<br>0: 20-80 | 1: Price > 20 EMA<br>-1: Price < 20 EMA |
| **1H/15m/5m**         | 1: MACD > Signal<br>-1: MACD < Signal | 1: RSI > 50<br>-1: RSI < 50             | 1: Price > 20 EMA<br>-1: Price < 20 EMA |

## Example

### Input Scenario

- **Timeframe:** 1 Hour
- **MACD:** MACD line at 0.05, Signal line at 0.02 (MACD above Signal)
- **RSI:** Currently at 65 (above 50)
- **Bollinger Bands:** Price candle closing at $50,200, 20 EMA at $49,800 (price above EMA)

### Output

```
Timeframe: 1H
M: 1  (MACD > Signal)
R: 1  (RSI > 50)
B: 1  (Price > 20 EMA)
Bias: Strong BUY (all indicators bullish)
```

### Another Example

**Input Scenario:**

- **Timeframe:** Daily
- **MACD:** MACD line at -0.03, Signal line at -0.01 (MACD below Signal)
- **RSI:** Currently at 15 (below 20, oversold)
- **Bollinger Bands:** Price candle closing at $48,500, 20 EMA at $49,200 (price below EMA)

**Output:**

```
Timeframe: Daily
M: -1  (MACD < Signal)
R: 1   (RSI < 20, oversold - reversal signal)
B: -1  (Price < 20 EMA)
Bias: Mixed (oversold but bearish structure)
```
