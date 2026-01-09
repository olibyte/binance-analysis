# Candlestick Pattern Recognition - Summary & Python Detection Code

A comprehensive reference for candlestick patterns and their Python detection algorithms, based on _Mastering Financial Pattern Recognition_ by Sofien Kaabar.

---

## Table of Contents

- [Candlestick Pattern Recognition - Summary \& Python Detection Code](#candlestick-pattern-recognition---summary--python-detection-code)
  - [Table of Contents](#table-of-contents)
  - [Trend-Following Patterns](#trend-following-patterns)
    - [1. Marubozu Pattern](#1-marubozu-pattern)
    - [2. Three Candles Pattern](#2-three-candles-pattern)
    - [3. Three Methods Pattern](#3-three-methods-pattern)
    - [4. Tasuki Pattern](#4-tasuki-pattern)
    - [5. Hikkake Pattern](#5-hikkake-pattern)
    - [6. Quintuplets Pattern](#6-quintuplets-pattern)
  - [Classic Contrarian Patterns](#classic-contrarian-patterns)
    - [7. Doji Pattern](#7-doji-pattern)
    - [8. Harami Pattern](#8-harami-pattern)
    - [9. Tweezers Pattern](#9-tweezers-pattern)
    - [10. Stick Sandwich Pattern](#10-stick-sandwich-pattern)
    - [11. Hammer Pattern](#11-hammer-pattern)
    - [12. Star Pattern](#12-star-pattern)
    - [13. Piercing Pattern](#13-piercing-pattern)
    - [14. Engulfing Pattern](#14-engulfing-pattern)
    - [15. Abandoned Baby Pattern](#15-abandoned-baby-pattern)
    - [16. Spinning Top Pattern](#16-spinning-top-pattern)
    - [17. Inside Up/Down Pattern](#17-inside-updown-pattern)
    - [18. Tower Pattern](#18-tower-pattern)
    - [19. On Neck Pattern](#19-on-neck-pattern)
  - [Modern Trend-Following Patterns](#modern-trend-following-patterns)
    - [20. Double Trouble Pattern](#20-double-trouble-pattern)
    - [21. Bottle Pattern](#21-bottle-pattern)
    - [22. Slingshot Pattern](#22-slingshot-pattern)
    - [23. H Pattern](#23-h-pattern)
  - [Modern Contrarian Patterns](#modern-contrarian-patterns)
    - [24. Doppelgänger Pattern](#24-doppelgänger-pattern)
    - [25. Blockade Pattern](#25-blockade-pattern)
    - [26. Euphoria Pattern](#26-euphoria-pattern)
    - [27. Barrier Pattern](#27-barrier-pattern)
    - [28. Mirror Pattern](#28-mirror-pattern)
    - [29. Shrinking Pattern](#29-shrinking-pattern)
  - [Trend-Following Strategies (Chapter 10)](#trend-following-strategies-chapter-10)
    - [Strategy 1: Double Trouble + RSI](#strategy-1-double-trouble--rsi)
    - [Strategy 2: Three Candles + Moving Average](#strategy-2-three-candles--moving-average)
    - [Strategy 3: Bottle + Stochastic Oscillator](#strategy-3-bottle--stochastic-oscillator)
    - [Strategy 4: Marubozu + K's Volatility Bands](#strategy-4-marubozu--ks-volatility-bands)
    - [Strategy 5: H Pattern + Trend Intensity Index (TII)](#strategy-5-h-pattern--trend-intensity-index-tii)
  - [Contrarian Strategies (Chapter 11)](#contrarian-strategies-chapter-11)
    - [Strategy 1: Doji + RSI](#strategy-1-doji--rsi)
    - [Strategy 2: Engulfing + Bollinger Bands](#strategy-2-engulfing--bollinger-bands)
    - [Strategy 3: Piercing + Stochastic Oscillator](#strategy-3-piercing--stochastic-oscillator)
    - [Strategy 4: Euphoria + K's Envelopes](#strategy-4-euphoria--ks-envelopes)
    - [Strategy 5: Barrier + RSI-ATR](#strategy-5-barrier--rsi-atr)
  - [Exit Techniques (Chapter 9)](#exit-techniques-chapter-9)
    - [The Symmetrical Exit Technique](#the-symmetrical-exit-technique)
    - [The Fixed Holding Period Exit](#the-fixed-holding-period-exit)
    - [The Variable Holding Period Exit](#the-variable-holding-period-exit)
    - [The Hybrid Exit Technique (Recommended)](#the-hybrid-exit-technique-recommended)
    - [Pattern Invalidation (Stop-Loss)](#pattern-invalidation-stop-loss)
  - [Alternative Charting Systems (Chapter 8)](#alternative-charting-systems-chapter-8)
    - [Heikin-Ashi System](#heikin-ashi-system)
    - [K's Candlesticks System](#ks-candlesticks-system)
    - [Comparison of Charting Systems](#comparison-of-charting-systems)
  - [Helper Functions](#helper-functions)
  - [Column Index Reference](#column-index-reference)
  - [Notes on Usage](#notes-on-usage)

---

## Trend-Following Patterns

### 1. Marubozu Pattern

**Summary:** A single-candle pattern with no wicks (shadows), indicating strong momentum. A bullish Marubozu has open = low and close = high. A bearish Marubozu has open = high and close = low. Represents maximum buying/selling pressure in one period.

**Psychology:** When a candle closes at its high with no lower wick, buyers dominated the entire session with no selling interest. The opposite applies for bearish.

```python
def signal(data, open_col, high_col, low_col, close_col, buy_col, sell_col):
    data = add_column(data, 5)

    for i in range(len(data)):
        try:
            # Bullish Marubozu: open == low AND close == high
            if (data[i, close_col] > data[i, open_col] and
                data[i, high_col] == data[i, close_col] and
                data[i, low_col] == data[i, open_col]):
                data[i + 1, buy_col] = 1

            # Bearish Marubozu: open == high AND close == low
            elif (data[i, close_col] < data[i, open_col] and
                  data[i, high_col] == data[i, open_col] and
                  data[i, low_col] == data[i, close_col]):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### 2. Three Candles Pattern

**Summary:** Also known as Three White Soldiers (bullish) or Three Black Crows (bearish). Three consecutive large candles of the same color, each closing higher/lower than the previous. Signals strong trend continuation through herding behavior.

**Psychology:** When three consecutive large candles appear in the same direction, it signals strong conviction and often triggers herding behavior as traders follow the momentum.

```python
def signal(data, open_col, close_col, buy_col, sell_col, body=0.0005):
    data = add_column(data, 5)

    for i in range(len(data)):
        try:
            # Bullish: Three consecutive bullish candles with body > threshold
            # Each close > previous close
            if (data[i, close_col] - data[i, open_col] > body and
                data[i-1, close_col] - data[i-1, open_col] > body and
                data[i-2, close_col] - data[i-2, open_col] > body and
                data[i, close_col] > data[i-1, close_col] and
                data[i-1, close_col] > data[i-2, close_col] and
                data[i-2, close_col] > data[i-3, close_col]):
                data[i + 1, buy_col] = 1

            # Bearish: Three consecutive bearish candles
            elif (data[i, open_col] - data[i, close_col] > body and
                  data[i-1, open_col] - data[i-1, close_col] > body and
                  data[i-2, open_col] - data[i-2, close_col] > body and
                  data[i, close_col] < data[i-1, close_col] and
                  data[i-1, close_col] < data[i-2, close_col] and
                  data[i-2, close_col] < data[i-3, close_col]):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### 3. Three Methods Pattern

**Summary:** A five-candle continuation pattern. Rising Three Methods: large bullish candle → three small bearish candles contained within the first → large bullish candle breaking out. Falling Three Methods is the bearish mirror.

**Psychology:** Represents a brief consolidation/retracement within a trend before continuation. The small candles show profit-taking, while the final candle confirms trend resumption.

```python
def signal(data, open_col, high_col, low_col, close_col, buy_col, sell_col):
    data = add_column(data, 5)

    for i in range(len(data)):
        try:
            # Rising Three Methods
            if (data[i, close_col] > data[i, open_col] and
                data[i, close_col] > data[i-4, high_col] and
                data[i, low_col] < data[i-1, low_col] and
                data[i-1, close_col] < data[i-4, close_col] and
                data[i-1, low_col] > data[i-4, low_col] and
                data[i-2, close_col] < data[i-4, close_col] and
                data[i-2, low_col] > data[i-4, low_col] and
                data[i-3, close_col] < data[i-4, close_col] and
                data[i-3, low_col] > data[i-4, low_col] and
                data[i-4, close_col] > data[i-4, open_col]):
                data[i + 1, buy_col] = 1

            # Falling Three Methods
            elif (data[i, close_col] < data[i, open_col] and
                  data[i, close_col] < data[i-4, low_col] and
                  data[i, high_col] > data[i-1, high_col] and
                  data[i-1, close_col] > data[i-4, close_col] and
                  data[i-1, high_col] < data[i-4, high_col] and
                  data[i-2, close_col] > data[i-4, close_col] and
                  data[i-2, high_col] < data[i-4, high_col] and
                  data[i-3, close_col] > data[i-4, close_col] and
                  data[i-3, high_col] < data[i-4, high_col] and
                  data[i-4, close_col] < data[i-4, open_col]):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### 4. Tasuki Pattern

**Summary:** A three-candle gap continuation pattern. Bullish: bearish candle → bullish candle gapping up → bearish candle closing within the gap but not filling it completely. Shows consolidation after a gap.

**Psychology:** The gap represents strong momentum, and the final candle failing to fill the gap confirms that the trend remains intact.

```python
def signal(data, open_col, high_col, low_col, close_col, buy_col, sell_col):
    data = add_column(data, 5)

    for i in range(len(data)):
        try:
            # Bullish Tasuki
            if (data[i, close_col] < data[i, open_col] and
                data[i, close_col] < data[i-1, open_col] and
                data[i, close_col] > data[i-2, close_col] and
                data[i-1, close_col] > data[i-1, open_col] and
                data[i-1, open_col] > data[i-2, close_col] and
                data[i-2, close_col] > data[i-2, open_col]):
                data[i + 1, buy_col] = 1

            # Bearish Tasuki
            elif (data[i, close_col] > data[i, open_col] and
                  data[i, close_col] > data[i-1, open_col] and
                  data[i, close_col] < data[i-2, close_col] and
                  data[i-1, close_col] < data[i-1, open_col] and
                  data[i-1, open_col] < data[i-2, close_col] and
                  data[i-2, close_col] < data[i-2, open_col]):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### 5. Hikkake Pattern

**Summary:** A five-candle pattern featuring a false breakout. Bullish: starts with bullish candle → bearish candle embedded inside → two bearish candles breaking below → breakout above validates the pattern.

**Psychology:** Traps traders on the wrong side of the market through a false breakout, then reverses.

```python
def signal(data, open_col, high_col, low_col, close_col, buy_col, sell_col):
    data = add_column(data, 5)

    for i in range(len(data)):
        try:
            # Bullish Hikkake
            if (data[i, close_col] > data[i-3, high_col] and
                data[i, close_col] > data[i-4, close_col] and
                data[i-1, low_col] < data[i, open_col] and
                data[i-1, close_col] < data[i, close_col] and
                data[i-1, high_col] <= data[i-3, high_col] and
                data[i-2, low_col] < data[i, open_col] and
                data[i-2, close_col] < data[i, close_col] and
                data[i-2, high_col] <= data[i-3, high_col] and
                data[i-3, high_col] < data[i-4, high_col] and
                data[i-3, low_col] > data[i-4, low_col] and
                data[i-4, close_col] > data[i-4, open_col]):
                data[i + 1, buy_col] = 1

            # Bearish Hikkake (mirror conditions)
            elif (data[i, close_col] < data[i-3, low_col] and
                  data[i, close_col] < data[i-4, close_col] and
                  data[i-1, high_col] > data[i, open_col] and
                  data[i-1, close_col] > data[i, close_col] and
                  data[i-1, low_col] >= data[i-3, low_col] and
                  data[i-2, high_col] > data[i, open_col] and
                  data[i-2, close_col] > data[i, close_col] and
                  data[i-2, low_col] >= data[i-3, low_col] and
                  data[i-3, low_col] > data[i-4, low_col] and
                  data[i-3, high_col] < data[i-4, high_col] and
                  data[i-4, close_col] < data[i-4, open_col]):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### 6. Quintuplets Pattern

**Summary:** Five consecutive small candles in the same direction, each closing progressively higher (bullish) or lower (bearish). Represents gradual but persistent movement.

**Psychology:** Shows sustained but cautious momentum, often indicating accumulation/distribution by larger players.

```python
def signal(data, open_col, close_col, buy_col, sell_col, body=0.0003):
    data = add_column(data, 5)

    for i in range(len(data)):
        try:
            # Bullish: 5 small bullish candles, each close > previous close
            if (data[i, close_col] > data[i, open_col] and
                data[i, close_col] - data[i, open_col] < body and
                data[i, close_col] > data[i-1, close_col] and
                data[i-1, close_col] > data[i-1, open_col] and
                data[i-1, close_col] - data[i-1, open_col] < body and
                data[i-1, close_col] > data[i-2, close_col] and
                data[i-2, close_col] > data[i-2, open_col] and
                data[i-2, close_col] - data[i-2, open_col] < body and
                data[i-2, close_col] > data[i-3, close_col] and
                data[i-3, close_col] > data[i-3, open_col] and
                data[i-3, close_col] - data[i-3, open_col] < body and
                data[i-3, close_col] > data[i-4, close_col] and
                data[i-4, close_col] > data[i-4, open_col] and
                data[i-4, close_col] - data[i-4, open_col] < body):
                data[i + 1, buy_col] = 1

            # Bearish: mirror conditions
            elif (data[i, close_col] < data[i, open_col] and
                  data[i, open_col] - data[i, close_col] < body and
                  # ... (similar pattern for 5 bearish candles)
                  True):  # Add full conditions
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

## Classic Contrarian Patterns

### 7. Doji Pattern

**Summary:** A single candle where open = close (or very close), creating a cross-like shape. Signals indecision and potential reversal. Variations include: Dragonfly Doji (long lower wick), Gravestone Doji (long upper wick), Flat Doji, Double Doji, and Tri Star Doji.

**Psychology:** Represents equilibrium between buyers and sellers. In a trend, it signals loss of momentum and potential reversal.

```python
def signal(data, open_col, close_col, buy_col, sell_col):
    data = add_column(data, 5)

    for i in range(len(data)):
        try:
            # Bullish Doji: Doji after downtrend, confirmed by bullish candle
            if (data[i, close_col] > data[i, open_col] and
                data[i, close_col] > data[i-1, close_col] and
                data[i-1, close_col] == data[i-1, open_col] and  # Doji
                data[i-2, close_col] < data[i-2, open_col]):     # Prior bearish
                data[i + 1, buy_col] = 1

            # Bearish Doji: Doji after uptrend, confirmed by bearish candle
            elif (data[i, close_col] < data[i, open_col] and
                  data[i, close_col] < data[i-1, close_col] and
                  data[i-1, close_col] == data[i-1, open_col] and  # Doji
                  data[i-2, close_col] > data[i-2, open_col]):     # Prior bullish
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### 8. Harami Pattern

**Summary:** A two-candle reversal pattern where the second candle's body is completely contained within the first candle's body. "Harami" means pregnant in Japanese. Flexible version: body contained. Strict version: entire candle (including wicks) contained.

**Psychology:** The shrinking candle size shows loss of conviction in the prevailing trend.

```python
# Flexible Harami
def signal(data, open_col, high_col, low_col, close_col, buy_col, sell_col):
    data = add_column(data, 5)

    for i in range(len(data)):
        try:
            # Bullish Harami: bearish mother → small bullish baby inside
            if (data[i, close_col] < data[i-1, open_col] and
                data[i, open_col] > data[i-1, close_col] and
                data[i, high_col] < data[i-1, high_col] and
                data[i, low_col] > data[i-1, low_col] and
                data[i, close_col] > data[i, open_col] and
                data[i-1, close_col] < data[i-1, open_col] and
                data[i-2, close_col] < data[i-2, open_col]):
                data[i + 1, buy_col] = 1

            # Bearish Harami: bullish mother → small bearish baby inside
            elif (data[i, close_col] > data[i-1, open_col] and
                  data[i, open_col] < data[i-1, close_col] and
                  data[i, high_col] < data[i-1, high_col] and
                  data[i, low_col] > data[i-1, low_col] and
                  data[i, close_col] < data[i, open_col] and
                  data[i-1, close_col] > data[i-1, open_col] and
                  data[i-2, close_col] > data[i-2, open_col]):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### 9. Tweezers Pattern

**Summary:** A two-candle pattern where consecutive candles share the same low (bullish Tweezers Bottom) or same high (bearish Tweezers Top). Signals support/resistance levels.

**Psychology:** When price fails to break the same level twice, it suggests strong support/resistance.

```python
def signal(data, open_col, high_col, low_col, close_col, buy_col, sell_col, body=0.0003):
    data = add_column(data, 5)

    for i in range(len(data)):
        try:
            # Bullish Tweezers: same low, bullish candle after bearish
            if (data[i, close_col] > data[i, open_col] and
                data[i, low_col] == data[i-1, low_col] and
                data[i, close_col] - data[i, open_col] < body and
                data[i-1, close_col] < data[i-1, open_col] and
                data[i-2, close_col] < data[i-2, open_col]):
                data[i + 1, buy_col] = 1

            # Bearish Tweezers: same high, bearish candle after bullish
            elif (data[i, close_col] < data[i, open_col] and
                  data[i, high_col] == data[i-1, high_col] and
                  data[i-1, close_col] > data[i-1, open_col] and
                  data[i-2, close_col] > data[i-2, open_col]):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### 10. Stick Sandwich Pattern

**Summary:** A three-candle pattern with two same-color outer candles "sandwiching" an opposite-color middle candle. The outer candles share similar price levels.

**Psychology:** The middle candle represents a failed attempt to continue in the opposite direction, trapped between the "bread" candles.

```python
def signal(data, open_col, high_col, low_col, close_col, buy_col, sell_col):
    data = add_column(data, 5)

    for i in range(len(data)):
        try:
            # Bullish Stick Sandwich
            if (data[i, close_col] < data[i, open_col] and
                data[i, high_col] > data[i-1, high_col] and
                data[i, low_col] < data[i-1, low_col] and
                data[i-1, close_col] > data[i-1, open_col] and
                data[i-2, close_col] < data[i-2, open_col] and
                data[i-2, high_col] > data[i-1, high_col] and
                data[i-2, low_col] < data[i-1, low_col] and
                data[i-2, close_col] < data[i-3, close_col] and
                data[i-3, close_col] < data[i-3, open_col]):
                data[i + 1, buy_col] = 1

            # Bearish Stick Sandwich (mirror conditions)
            elif (data[i, close_col] > data[i, open_col] and
                  data[i, high_col] > data[i-1, high_col] and
                  data[i, low_col] < data[i-1, low_col] and
                  data[i-1, close_col] < data[i-1, open_col] and
                  data[i-2, close_col] > data[i-2, open_col] and
                  data[i-2, high_col] > data[i-1, high_col] and
                  data[i-2, low_col] < data[i-1, low_col]):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### 11. Hammer Pattern

**Summary:** A single candle with a small body near the top and a long lower shadow (at least 2x the body). No or minimal upper shadow. Signals potential reversal when appearing after a downtrend. Inverted Hammer is the opposite (long upper shadow).

**Psychology:** Sellers pushed price down significantly, but buyers regained control by the close, showing rejection of lower prices.

```python
def signal(data, open_col, high_col, low_col, close_col, buy_col, sell_col, body=0.0003, wick=0.0005):
    data = add_column(data, 5)

    for i in range(len(data)):
        try:
            # Bullish Hammer: small body, long lower wick, close == high
            if (data[i, close_col] > data[i, open_col] and
                abs(data[i-1, close_col] - data[i-1, open_col]) < body and
                min(data[i-1, close_col], data[i-1, open_col]) - data[i-1, low_col] > 2 * wick and
                data[i-1, close_col] == data[i-1, high_col] and
                data[i-2, close_col] < data[i-2, open_col]):
                data[i + 1, buy_col] = 1

            # Bearish Hammer (Inverted): small body, long upper wick
            elif (data[i, close_col] < data[i, open_col] and
                  abs(data[i-1, close_col] - data[i-1, open_col]) < body and
                  data[i-1, high_col] - max(data[i-1, close_col], data[i-1, open_col]) > 2 * wick and
                  data[i-1, close_col] == data[i-1, low_col] and
                  data[i-2, close_col] > data[i-2, open_col]):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### 12. Star Pattern

**Summary:** A three-candle pattern. **Morning Star** (bullish): bearish candle → small gapped-down candle → bullish candle. **Evening Star** (bearish): bullish candle → small gapped-up candle → bearish candle. The middle candle is isolated (gaps from both).

**Psychology:** The gap and reversal show exhaustion of the prior trend and strong counter-momentum.

```python
def signal(data, open_col, high_col, low_col, close_col, buy_col, sell_col):
    data = add_column(data, 5)

    for i in range(len(data)):
        try:
            # Morning Star
            if (data[i, close_col] > data[i, open_col] and
                max(data[i-1, close_col], data[i-1, open_col]) < data[i, open_col] and
                max(data[i-1, close_col], data[i-1, open_col]) < data[i-2, close_col] and
                data[i-2, close_col] < data[i-2, open_col]):
                data[i + 1, buy_col] = 1

            # Evening Star
            elif (data[i, close_col] < data[i, open_col] and
                  min(data[i-1, close_col], data[i-1, open_col]) > data[i, open_col] and
                  min(data[i-1, close_col], data[i-1, open_col]) > data[i-2, close_col] and
                  data[i-2, close_col] > data[i-2, open_col]):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### 13. Piercing Pattern

**Summary:** A two-candle bullish reversal. First candle is bearish, second is bullish that opens below the first's close but closes above the midpoint of the first candle (but not above its open). **Dark Cloud Cover** is the bearish mirror.

**Psychology:** The gap down followed by strong buying that penetrates the prior candle shows buyers overwhelming sellers.

```python
def signal(data, open_col, close_col, buy_col, sell_col):
    data = add_column(data, 5)

    for i in range(len(data)):
        try:
            # Bullish Piercing
            if (data[i, close_col] > data[i, open_col] and
                data[i, close_col] < data[i-1, open_col] and
                data[i, close_col] > data[i-1, close_col] and
                data[i, open_col] < data[i-1, close_col] and
                data[i-1, close_col] < data[i-1, open_col] and
                data[i-2, close_col] < data[i-2, open_col]):
                data[i + 1, buy_col] = 1

            # Bearish Dark Cloud Cover
            elif (data[i, close_col] < data[i, open_col] and
                  data[i, close_col] > data[i-1, open_col] and
                  data[i, close_col] < data[i-1, close_col] and
                  data[i, open_col] > data[i-1, close_col] and
                  data[i-1, close_col] > data[i-1, open_col] and
                  data[i-2, close_col] > data[i-2, open_col]):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### 14. Engulfing Pattern

**Summary:** A two-candle reversal pattern where the second candle's body completely engulfs the first candle's body. Bullish Engulfing: bearish → larger bullish. Bearish Engulfing: bullish → larger bearish.

**Psychology:** The complete eclipse of the first candle by the second shows a dramatic shift in sentiment and control.

```python
def signal(data, open_col, close_col, buy_col, sell_col):
    data = add_column(data, 5)

    for i in range(len(data)):
        try:
            # Bullish Engulfing
            if (data[i, close_col] > data[i, open_col] and
                data[i, open_col] < data[i-1, close_col] and
                data[i, close_col] > data[i-1, open_col] and
                data[i-1, close_col] < data[i-1, open_col] and
                data[i-2, close_col] < data[i-2, open_col]):
                data[i + 1, buy_col] = 1

            # Bearish Engulfing
            elif (data[i, close_col] < data[i, open_col] and
                  data[i, open_col] > data[i-1, close_col] and
                  data[i, close_col] < data[i-1, open_col] and
                  data[i-1, close_col] > data[i-1, open_col] and
                  data[i-2, close_col] > data[i-2, open_col]):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### 15. Abandoned Baby Pattern

**Summary:** A rare three-candle reversal pattern. Bullish: bearish candle → Doji that gaps below (no overlap) → bullish candle that gaps above the Doji. Extremely rare in practice.

**Psychology:** The isolated Doji represents complete exhaustion, and the subsequent gap in the opposite direction confirms the reversal.

```python
def signal(data, open_col, high_col, low_col, close_col, buy_col, sell_col):
    data = add_column(data, 5)

    for i in range(len(data)):
        try:
            # Bullish Abandoned Baby
            if (data[i, close_col] > data[i, open_col] and
                data[i-1, close_col] == data[i-1, open_col] and  # Doji
                data[i-1, high_col] < data[i, low_col] and       # Gap up from Doji
                data[i-1, high_col] < data[i-2, low_col] and     # Gap down to Doji
                data[i-2, close_col] < data[i-2, open_col]):
                data[i + 1, buy_col] = 1

            # Bearish Abandoned Baby
            elif (data[i, close_col] < data[i, open_col] and
                  data[i-1, close_col] == data[i-1, open_col] and  # Doji
                  data[i-1, low_col] > data[i, high_col] and       # Gap down from Doji
                  data[i-1, low_col] > data[i-2, high_col] and     # Gap up to Doji
                  data[i-2, close_col] > data[i-2, open_col]):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### 16. Spinning Top Pattern

**Summary:** A three-candle reversal similar to Doji but more common. Features a small body with wicks on both sides, followed by confirmation. Indicates indecision with potential volatility increase.

**Psychology:** Small body with long shadows shows intense battle between buyers and sellers with no clear winner.

```python
def signal(data, open_col, high_col, low_col, close_col, buy_col, sell_col, body=0.0003, wick=0.0003):
    data = add_column(data, 5)

    for i in range(len(data)):
        try:
            # Bullish Spinning Top (after bearish trend, confirmed by bullish)
            if (data[i, close_col] - data[i, open_col] > body and
                data[i-1, high_col] - data[i-1, close_col] >= wick and
                data[i-1, open_col] - data[i-1, low_col] >= wick and
                data[i-1, close_col] - data[i-1, open_col] < body and
                data[i-1, close_col] > data[i-1, open_col] and
                data[i-2, close_col] < data[i-2, open_col] and
                data[i-2, open_col] - data[i-2, close_col] > body):
                data[i + 1, buy_col] = 1

            # Bearish Spinning Top (mirror conditions)
            elif (data[i, open_col] - data[i, close_col] > body and
                  data[i-1, high_col] - data[i-1, open_col] >= wick and
                  data[i-1, close_col] - data[i-1, low_col] >= wick and
                  data[i-1, open_col] - data[i-1, close_col] < body and
                  data[i-1, close_col] < data[i-1, open_col] and
                  data[i-2, close_col] > data[i-2, open_col]):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### 17. Inside Up/Down Pattern

**Summary:** A three-candle reversal pattern. **Inside Up** (bullish): bearish candle → smaller bullish candle inside → bullish confirmation breaking above the first. Similar to a confirmed Harami.

**Psychology:** The inside bar shows consolidation, and the breakout candle confirms the reversal direction.

```python
def signal(data, open_col, high_col, low_col, close_col, buy_col, sell_col, body=0.0003):
    data = add_column(data, 5)

    for i in range(len(data)):
        try:
            # Inside Up (Bullish)
            if (data[i-2, close_col] < data[i-2, open_col] and
                abs(data[i-2, open_col] - data[i-2, close_col]) > body and
                data[i-1, close_col] < data[i-2, open_col] and
                data[i-1, open_col] > data[i-2, close_col] and
                data[i-1, close_col] > data[i-1, open_col] and
                data[i, close_col] > data[i-2, open_col] and
                data[i, close_col] > data[i, open_col] and
                abs(data[i, open_col] - data[i, close_col]) > body):
                data[i + 1, buy_col] = 1

            # Inside Down (Bearish)
            elif (data[i-2, close_col] > data[i-2, open_col] and
                  abs(data[i-2, close_col] - data[i-2, open_col]) > body and
                  data[i-1, close_col] > data[i-2, open_col] and
                  data[i-1, open_col] < data[i-2, close_col] and
                  data[i-1, close_col] < data[i-1, open_col] and
                  data[i, close_col] < data[i-2, open_col] and
                  data[i, close_col] < data[i, open_col] and
                  abs(data[i, open_col] - data[i, close_col]) > body):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### 18. Tower Pattern

**Summary:** A five-candle stabilization/reversal pattern. **Tower Bottom**: bearish candle → three small range-bound candles → bullish confirmation. Shows gradual transition from selling to buying pressure.

**Psychology:** The small candles represent stabilization after a move, and the final candle confirms the reversal.

```python
def signal(data, open_col, high_col, low_col, close_col, buy_col, sell_col, body=0.0003):
    data = add_column(data, 5)

    for i in range(len(data)):
        try:
            # Tower Bottom (Bullish)
            if (data[i, close_col] > data[i, open_col] and
                data[i, close_col] - data[i, open_col] > body and
                data[i-2, low_col] < data[i-1, low_col] and
                data[i-2, low_col] < data[i-3, low_col] and
                data[i-4, close_col] < data[i-4, open_col] and
                data[i-4, open_col] - data[i, close_col] > body):
                data[i + 1, buy_col] = 1

            # Tower Top (Bearish)
            elif (data[i, close_col] < data[i, open_col] and
                  data[i, open_col] - data[i, close_col] > body and
                  data[i-2, high_col] > data[i-1, high_col] and
                  data[i-2, high_col] > data[i-3, high_col] and
                  data[i-4, close_col] > data[i-4, open_col] and
                  data[i-4, close_col] - data[i, open_col] > body):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### 19. On Neck Pattern

**Summary:** A two-candle pattern where the second candle closes exactly at the close of the first candle. Bullish: bearish candle → bullish candle closing at previous close. Shows support/resistance at that level.

**Psychology:** The precise close at the same level indicates a key price point being tested.

```python
def signal(data, open_col, high_col, low_col, close_col, buy_col, sell_col):
    data = add_column(data, 5)

    for i in range(len(data)):
        try:
            # Bullish On Neck
            if (data[i, close_col] > data[i, open_col] and
                data[i, close_col] == data[i-1, close_col] and
                data[i, open_col] < data[i-1, close_col] and
                data[i-1, close_col] < data[i-1, open_col]):
                data[i + 1, buy_col] = 1

            # Bearish On Neck
            elif (data[i, close_col] < data[i, open_col] and
                  data[i, close_col] == data[i-1, close_col] and
                  data[i, open_col] > data[i-1, close_col] and
                  data[i-1, close_col] > data[i-1, open_col]):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

## Modern Trend-Following Patterns

### 20. Double Trouble Pattern

**Summary:** A two-candle trend-following pattern that uses the Average True Range (ATR) for validation. Requires two consecutive same-color candles where the second candle's range exceeds 2x the ATR and its body is larger than the first candle's body.

**Psychology:** Large candles during trending periods indicate strong momentum and conviction. The ATR filter ensures the move is significant relative to recent volatility.

```python
def signal(data, open_col, high_col, low_col, close_col, atr_col, buy_col, sell_col):
    data = add_column(data, 5)

    for i in range(len(data)):
        try:
            # Bullish pattern
            if (data[i, close_col] > data[i, open_col] and
                data[i, close_col] > data[i-1, close_col] and
                data[i-1, close_col] > data[i-1, open_col] and
                data[i, high_col] - data[i, low_col] > (2 * data[i-1, atr_col]) and
                data[i, close_col] - data[i, open_col] > data[i-1, close_col] - data[i-1, open_col]):
                data[i + 1, buy_col] = 1

            # Bearish pattern
            elif (data[i, close_col] < data[i, open_col] and
                  data[i, close_col] < data[i-1, close_col] and
                  data[i-1, close_col] < data[i-1, open_col] and
                  data[i, high_col] - data[i, low_col] > (2 * data[i-1, atr_col]) and
                  data[i, open_col] - data[i, close_col] > data[i-1, open_col] - data[i-1, close_col]):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### 21. Bottle Pattern

**Summary:** A two-candle continuation pattern. Bullish: bullish candle → bullish candle with no low wick (open = low) that gaps below the previous close. The "bottle" shape comes from having a wick only on one side.

**Psychology:** The gap down followed by strong buying that closes higher, without making new lows, shows buyers stepping in aggressively at the open.

```python
def signal(data, open_col, high_col, low_col, close_col, buy_col, sell_col):
    data = add_column(data, 5)

    for i in range(len(data)):
        try:
            # Bullish Bottle: open == low, gaps below previous close
            if (data[i, close_col] > data[i, open_col] and
                data[i, open_col] == data[i, low_col] and
                data[i-1, close_col] > data[i-1, open_col] and
                data[i, open_col] < data[i-1, close_col]):
                data[i + 1, buy_col] = 1

            # Bearish Bottle: open == high, gaps above previous close
            elif (data[i, close_col] < data[i, open_col] and
                  data[i, open_col] == data[i, high_col] and
                  data[i-1, close_col] < data[i-1, open_col] and
                  data[i, open_col] > data[i-1, close_col]):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### 22. Slingshot Pattern

**Summary:** A four-candle breakout/pullback continuation pattern. Bullish: two bullish candles establishing trend → two pullback candles → final candle breaks above the second candle's high with low touching/below the first candle's high.

**Psychology:** Represents a healthy pullback within a trend followed by continuation, validating the trend's strength through the "slingshot" breakout.

```python
def signal(data, open_col, high_col, low_col, close_col, buy_col, sell_col):
    data = add_column(data, 5)

    for i in range(len(data)):
        try:
            # Bullish Slingshot
            if (data[i, close_col] > data[i-1, high_col] and
                data[i, close_col] > data[i-2, high_col] and
                data[i, low_col] <= data[i-3, high_col] and
                data[i, close_col] > data[i, open_col] and
                data[i-1, close_col] >= data[i-3, high_col] and
                data[i-2, low_col] >= data[i-3, low_col] and
                data[i-2, close_col] > data[i-2, open_col] and
                data[i-2, close_col] > data[i-3, high_col] and
                data[i-1, high_col] <= data[i-2, high_col]):
                data[i + 1, buy_col] = 1

            # Bearish Slingshot
            elif (data[i, close_col] < data[i-1, low_col] and
                  data[i, close_col] < data[i-2, low_col] and
                  data[i, high_col] >= data[i-3, low_col] and
                  data[i, close_col] < data[i, open_col] and
                  data[i-1, high_col] <= data[i-3, high_col] and
                  data[i-2, close_col] <= data[i-3, low_col] and
                  data[i-2, close_col] < data[i-2, open_col] and
                  data[i-2, close_col] < data[i-3, low_col] and
                  data[i-1, low_col] >= data[i-2, low_col]):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### 23. H Pattern

**Summary:** A three-candle continuation pattern featuring a Doji (indecision candle) in the middle. Bullish: bullish candle → Doji (open = close) → bullish candle closing above the Doji with higher low.

**Psychology:** The Doji represents a brief pause/consolidation within the trend, with the third candle confirming continuation.

```python
def signal(data, open_col, high_col, low_col, close_col, buy_col, sell_col):
    data = add_column(data, 5)

    for i in range(len(data)):
        try:
            # Bullish H pattern
            if (data[i, close_col] > data[i, open_col] and
                data[i, close_col] > data[i-1, close_col] and
                data[i, low_col] > data[i-1, low_col] and
                data[i-1, close_col] == data[i-1, open_col] and  # Doji
                data[i-2, close_col] > data[i-2, open_col] and
                data[i-2, high_col] < data[i-1, high_col]):
                data[i + 1, buy_col] = 1

            # Bearish H pattern
            elif (data[i, close_col] < data[i, open_col] and
                  data[i, close_col] < data[i-1, close_col] and
                  data[i, low_col] < data[i-1, low_col] and
                  data[i-1, close_col] == data[i-1, open_col] and  # Doji
                  data[i-2, close_col] < data[i-2, open_col] and
                  data[i-2, low_col] > data[i-1, low_col]):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

## Modern Contrarian Patterns

### 24. Doppelgänger Pattern

**Summary:** A three-candle reversal pattern featuring two identical "twin" candles. Bullish: bearish candle → two candles with same highs and lows (the "twins"). Requires rounding for practical detection.

**Psychology:** The twin candles represent indecision and equilibrium at a potential reversal zone, similar to double support/resistance.

```python
def signal(data, open_col, high_col, low_col, close_col, buy_col, sell_col):
    data = add_column(data, 5)
    data = rounding(data, 4)  # Round to 4 decimals for FX

    for i in range(len(data)):
        try:
            # Bullish Doppelgänger
            if (data[i-2, close_col] < data[i-2, open_col] and
                data[i-1, close_col] < data[i-2, open_col] and
                data[i, high_col] == data[i-1, high_col] and
                data[i, low_col] == data[i-1, low_col]):
                data[i + 1, buy_col] = 1

            # Bearish Doppelgänger
            elif (data[i-2, close_col] > data[i-2, open_col] and
                  data[i-1, close_col] > data[i-2, open_col] and
                  data[i, high_col] == data[i-1, high_col] and
                  data[i, low_col] == data[i-1, low_col]):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### 25. Blockade Pattern

**Summary:** A four-candle reversal pattern showing stabilization at support/resistance. Bullish: bearish candle → three candles with lows between the first candle's low and close → fourth bullish candle breaking above the first's high.

**Psychology:** The three candles forming within a zone show the market finding support, with the breakout confirming reversal.

```python
def signal(data, open_col, high_col, low_col, close_col, buy_col, sell_col):
    data = add_column(data, 5)

    for i in range(len(data)):
        try:
            # Bullish Blockade
            if (data[i-3, close_col] < data[i-3, open_col] and
                data[i-2, close_col] < data[i-3, open_col] and
                data[i-2, low_col] >= data[i-3, low_col] and
                data[i-2, low_col] <= data[i-3, close_col] and
                data[i-1, low_col] >= data[i-3, low_col] and
                data[i-1, low_col] <= data[i-3, close_col] and
                data[i, low_col] >= data[i-3, low_col] and
                data[i, low_col] <= data[i-3, close_col] and
                data[i, close_col] > data[i, open_col] and
                data[i, close_col] > data[i-3, high_col]):
                data[i + 1, buy_col] = 1

            # Bearish Blockade
            elif (data[i-3, close_col] > data[i-3, open_col] and
                  data[i-2, close_col] > data[i-3, open_col] and
                  data[i-2, high_col] <= data[i-3, high_col] and
                  data[i-2, high_col] >= data[i-3, close_col] and
                  data[i-1, high_col] <= data[i-3, high_col] and
                  data[i-1, high_col] >= data[i-3, close_col] and
                  data[i, high_col] <= data[i-3, high_col] and
                  data[i, high_col] >= data[i-3, close_col] and
                  data[i, close_col] < data[i, open_col] and
                  data[i, close_col] < data[i-3, low_col]):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### 26. Euphoria Pattern

**Summary:** A three-candle contrarian pattern similar to Three Candles but with increasing candle sizes. Bullish: three bearish candles, each larger than the previous. The increasing size signals exhaustion/climax.

**Psychology:** Accelerating price moves often indicate climax/exhaustion as late participants pile in, making reversals more likely.

```python
def signal(data, open_col, close_col, buy_col, sell_col):
    data = add_column(data, 5)
    data = rounding(data, 4)

    for i in range(len(data)):
        try:
            # Bullish Euphoria (after bearish exhaustion)
            if (data[i, open_col] > data[i, close_col] and
                data[i-1, open_col] > data[i-1, close_col] and
                data[i-2, open_col] > data[i-2, close_col] and
                data[i, close_col] < data[i-1, close_col] and
                data[i-1, close_col] < data[i-2, close_col] and
                (data[i, open_col] - data[i, close_col]) >
                (data[i-1, open_col] - data[i-1, close_col]) and
                (data[i-1, open_col] - data[i-1, close_col]) >
                (data[i-2, open_col] - data[i-2, close_col])):
                data[i + 1, buy_col] = 1

            # Bearish Euphoria (after bullish exhaustion)
            elif (data[i, open_col] < data[i, close_col] and
                  data[i-1, open_col] < data[i-1, close_col] and
                  data[i-2, open_col] < data[i-2, close_col] and
                  data[i, close_col] > data[i-1, close_col] and
                  data[i-1, close_col] > data[i-2, close_col] and
                  (data[i, close_col] - data[i, open_col]) >
                  (data[i-1, close_col] - data[i-1, open_col]) and
                  (data[i-1, close_col] - data[i-1, open_col]) >
                  (data[i-2, close_col] - data[i-2, open_col])):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### 27. Barrier Pattern

**Summary:** A simplified three-candle version of the Blockade pattern. Bullish: two bearish candles → one bullish candle, all with the same low (support). Requires rounding.

**Psychology:** Three candles finding support at the same level confirms strong demand at that price.

```python
def signal(data, open_col, high_col, low_col, close_col, buy_col, sell_col):
    data = add_column(data, 5)
    data = rounding(data, 4)  # Round for equal price matching

    for i in range(len(data)):
        try:
            # Bullish Barrier: same lows, last candle bullish
            if (data[i, close_col] > data[i, open_col] and
                data[i-1, close_col] < data[i-1, open_col] and
                data[i-2, close_col] < data[i-2, open_col] and
                data[i, low_col] == data[i-1, low_col] and
                data[i, low_col] == data[i-2, low_col]):
                data[i + 1, buy_col] = 1

            # Bearish Barrier: same highs, last candle bearish
            elif (data[i, close_col] < data[i, open_col] and
                  data[i-1, close_col] > data[i-1, open_col] and
                  data[i-2, close_col] > data[i-2, open_col] and
                  data[i, high_col] == data[i-1, high_col] and
                  data[i, high_col] == data[i-2, high_col]):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### 28. Mirror Pattern

**Summary:** A four-candle U-turn reversal pattern. Bullish: bearish candle → two candles with equal closes → bullish candle with high matching the first candle's high.

**Psychology:** The pattern represents price making a symmetric reversal, with the final candle "mirroring" back to the starting level.

```python
def signal(data, open_col, high_col, low_col, close_col, buy_col, sell_col):
    data = add_column(data, 5)
    data = rounding(data, 4)

    for i in range(len(data)):
        try:
            # Bullish Mirror
            if (data[i, close_col] > data[i, open_col] and
                data[i, high_col] == data[i-3, high_col] and
                data[i, close_col] > data[i-1, close_col] and
                data[i, close_col] > data[i-2, close_col] and
                data[i, close_col] > data[i-3, close_col] and
                data[i-3, close_col] < data[i-3, open_col] and
                data[i-1, close_col] == data[i-2, close_col]):
                data[i + 1, buy_col] = 1

            # Bearish Mirror
            elif (data[i, close_col] < data[i, open_col] and
                  data[i, low_col] == data[i-3, low_col] and
                  data[i, close_col] < data[i-1, close_col] and
                  data[i, close_col] < data[i-2, close_col] and
                  data[i, close_col] < data[i-3, close_col] and
                  data[i-3, close_col] > data[i-3, open_col] and
                  data[i-1, close_col] == data[i-2, close_col]):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### 29. Shrinking Pattern

**Summary:** A five-candle breakout pattern after congestion. Bullish: bearish candle → three progressively smaller candles → bullish breakout candle surpassing the second candle's high.

**Psychology:** Decreasing volatility (shrinking candles) often precedes breakouts. The pattern identifies compression followed by expansion.

```python
def signal(data, open_col, high_col, low_col, close_col, buy_col, sell_col):
    data = add_column(data, 5)
    data = rounding(data, 4)

    for i in range(len(data)):
        try:
            # Bullish Shrinking
            if (data[i-4, close_col] < data[i-4, open_col] and
                data[i, close_col] > data[i, open_col] and
                data[i, close_col] > data[i-3, high_col] and
                abs(data[i-3, close_col] - data[i-3, open_col]) <
                abs(data[i-4, close_col] - data[i-4, open_col]) and
                abs(data[i-2, close_col] - data[i-2, open_col]) <
                abs(data[i-3, close_col] - data[i-3, open_col]) and
                abs(data[i-1, close_col] - data[i-1, open_col]) <
                abs(data[i-2, close_col] - data[i-2, open_col]) and
                data[i-1, high_col] < data[i-2, high_col] and
                data[i-2, high_col] < data[i-3, high_col]):
                data[i + 1, buy_col] = 1

            # Bearish Shrinking
            elif (data[i-4, close_col] > data[i-4, open_col] and
                  data[i, close_col] < data[i, open_col] and
                  data[i, close_col] < data[i-3, low_col] and
                  abs(data[i-3, close_col] - data[i-3, open_col]) <
                  abs(data[i-4, close_col] - data[i-4, open_col]) and
                  abs(data[i-2, close_col] - data[i-2, open_col]) <
                  abs(data[i-3, close_col] - data[i-3, open_col]) and
                  abs(data[i-1, close_col] - data[i-1, open_col]) <
                  abs(data[i-2, close_col] - data[i-2, open_col]) and
                  data[i-1, low_col] > data[i-2, low_col] and
                  data[i-2, low_col] > data[i-3, low_col]):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

## Trend-Following Strategies (Chapter 10)

Candlestick patterns alone rarely provide stable returns. These strategies combine patterns with technical indicators to filter signals and increase conviction.

### Strategy 1: Double Trouble + RSI

**Concept:** Use RSI as a trend filter—only take signals aligned with the trend direction.

**Conditions:**

- **Long:** Bullish Double Trouble + RSI(14) > 50
- **Short:** Bearish Double Trouble + RSI(14) < 50

```python
def signal(data, open_col, high_col, low_col, close_col, atr_col, rsi_col, buy_col, sell_col):
    data = add_column(data, 5)
    for i in range(len(data)):
        try:
            # Bullish: Double Trouble + RSI above 50
            if (data[i, close_col] > data[i, open_col] and
                data[i, close_col] > data[i-1, close_col] and
                data[i-1, close_col] > data[i-1, open_col] and
                data[i, high_col] - data[i, low_col] > (2 * data[i-1, atr_col]) and
                data[i, close_col] - data[i, open_col] > data[i-1, close_col] - data[i-1, open_col] and
                data[i, rsi_col] > 50):
                data[i + 1, buy_col] = 1
            # Bearish: Double Trouble + RSI below 50
            elif (data[i, close_col] < data[i, open_col] and
                  data[i, close_col] < data[i-1, close_col] and
                  data[i-1, close_col] < data[i-1, open_col] and
                  data[i, high_col] - data[i, low_col] > (2 * data[i-1, atr_col]) and
                  data[i, open_col] - data[i, close_col] > data[i-1, open_col] - data[i-1, close_col] and
                  data[i, rsi_col] < 50):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### Strategy 2: Three Candles + Moving Average

**Concept:** Use a 100-period MA as trend filter. Only take bullish signals above MA, bearish below.

**Conditions:**

- **Long:** Three White Soldiers + Close > MA(100)
- **Short:** Three Black Crows + Close < MA(100)

```python
def signal(data, open_col, close_col, ma_col, buy_col, sell_col):
    body = 0  # Minimum body size threshold
    data = add_column(data, 10)
    for i in range(len(data)):
        try:
            # Bullish: Three White Soldiers above MA
            if (data[i, close_col] - data[i, open_col] > body and
                data[i-1, close_col] - data[i-1, open_col] > body and
                data[i-2, close_col] - data[i-2, open_col] > body and
                data[i, close_col] > data[i-1, close_col] and
                data[i-1, close_col] > data[i-2, close_col] and
                data[i, close_col] > data[i, ma_col]):
                data[i + 1, buy_col] = 1
            # Bearish: Three Black Crows below MA
            elif (data[i, open_col] - data[i, close_col] > body and
                  data[i-1, open_col] - data[i-1, close_col] > body and
                  data[i-2, open_col] - data[i-2, close_col] > body and
                  data[i, close_col] < data[i-1, close_col] and
                  data[i-1, close_col] < data[i-2, close_col] and
                  data[i, close_col] < data[i, ma_col]):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### Strategy 3: Bottle + Stochastic Oscillator

**Concept:** Use stochastic crossover as momentum confirmation for Bottle pattern signals.

**Conditions:**

- **Long:** Bullish Bottle + Stochastic > Signal Line
- **Short:** Bearish Bottle + Stochastic < Signal Line

```python
def signal(data, open_col, high_col, low_col, close_col, stoch_col, signal_col, buy_col, sell_col):
    data = add_column(data, 5)
    for i in range(len(data)):
        try:
            # Bullish Bottle + Stochastic above signal
            if (data[i, close_col] > data[i, open_col] and
                data[i, open_col] == data[i, low_col] and
                data[i-1, close_col] > data[i-1, open_col] and
                data[i, open_col] < data[i-1, close_col] and
                data[i, stoch_col] > data[i, signal_col]):
                data[i + 1, buy_col] = 1
            # Bearish Bottle + Stochastic below signal
            elif (data[i, close_col] < data[i, open_col] and
                  data[i, open_col] == data[i, high_col] and
                  data[i-1, close_col] < data[i-1, open_col] and
                  data[i, open_col] > data[i-1, close_col] and
                  data[i, stoch_col] < data[i, signal_col]):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### Strategy 4: Marubozu + K's Volatility Bands

**Concept:** Trade Marubozu patterns when price is on the opposite side of the middle band (mean reversion within trend).

**Conditions:**

- **Long:** Bullish Marubozu + Close < Middle Band
- **Short:** Bearish Marubozu + Close > Middle Band

```python
def signal(data, open_col, high_col, low_col, close_col, middle_band, buy_col, sell_col):
    data = add_column(data, 5)
    for i in range(len(data)):
        try:
            # Bullish Marubozu below middle band
            if (data[i, close_col] > data[i, open_col] and
                data[i, high_col] == data[i, close_col] and
                data[i, low_col] == data[i, open_col] and
                data[i, close_col] < data[i, middle_band]):
                data[i + 1, buy_col] = 1
            # Bearish Marubozu above middle band
            elif (data[i, close_col] < data[i, open_col] and
                  data[i, high_col] == data[i, open_col] and
                  data[i, low_col] == data[i, close_col] and
                  data[i, close_col] > data[i, middle_band]):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### Strategy 5: H Pattern + Trend Intensity Index (TII)

**Concept:** Use TII to confirm trend strength before taking H pattern continuation signals.

**Conditions:**

- **Long:** Bullish H Pattern + TII(20) > 50
- **Short:** Bearish H Pattern + TII(20) < 50

```python
def signal(data, open_col, high_col, low_col, close_col, tii_col, buy_col, sell_col):
    data = add_column(data, 5)
    data = rounding(data, 4)
    for i in range(len(data)):
        try:
            # Bullish H pattern + strong bullish TII
            if (data[i, close_col] > data[i, open_col] and
                data[i, close_col] > data[i-1, close_col] and
                data[i, low_col] > data[i-1, low_col] and
                data[i-1, close_col] == data[i-1, open_col] and  # Doji
                data[i-2, close_col] > data[i-2, open_col] and
                data[i, tii_col] > 50):
                data[i + 1, buy_col] = 1
            # Bearish H pattern + strong bearish TII
            elif (data[i, close_col] < data[i, open_col] and
                  data[i, close_col] < data[i-1, close_col] and
                  data[i, low_col] < data[i-1, low_col] and
                  data[i-1, close_col] == data[i-1, open_col] and  # Doji
                  data[i-2, close_col] < data[i-2, open_col] and
                  data[i, tii_col] < 50):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

## Contrarian Strategies (Chapter 11)

Contrarian strategies look for reversals at extreme levels. They work best in ranging/sideways markets.

### Strategy 1: Doji + RSI

**Concept:** Combine the simplest reversal pattern (Doji) with RSI at extreme levels.

**Conditions:**

- **Long:** Doji (open = close) + RSI(3) < 20
- **Short:** Doji (open = close) + RSI(3) > 80

```python
lower_barrier = 20
upper_barrier = 80

def signal(data, open_col, close_col, rsi_col, buy_col, sell_col):
    data = add_column(data, 5)
    data = rounding(data, 0)
    for i in range(len(data)):
        try:
            # Bullish: Doji at oversold
            if (data[i, close_col] == data[i, open_col] and
                data[i, rsi_col] < lower_barrier):
                data[i + 1, buy_col] = 1
            # Bearish: Doji at overbought
            elif (data[i, close_col] == data[i, open_col] and
                  data[i, rsi_col] > upper_barrier):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### Strategy 2: Engulfing + Bollinger Bands

**Concept:** Trade Engulfing patterns when price breaks outside Bollinger Bands (statistical extremes).

**Conditions:**

- **Long:** Bullish Engulfing + Close < Lower Band
- **Short:** Bearish Engulfing + Close > Upper Band

```python
def signal(data, open_col, close_col, upper_band, lower_band, buy_col, sell_col):
    data = add_column(data, 5)
    for i in range(len(data)):
        try:
            # Bullish Engulfing below lower band
            if (data[i, close_col] > data[i, open_col] and
                data[i, open_col] < data[i-1, close_col] and
                data[i, close_col] > data[i-1, open_col] and
                data[i-1, close_col] < data[i-1, open_col] and
                data[i, close_col] < data[i, lower_band]):
                data[i + 1, buy_col] = 1
            # Bearish Engulfing above upper band
            elif (data[i, close_col] < data[i, open_col] and
                  data[i, open_col] > data[i-1, close_col] and
                  data[i, close_col] < data[i-1, open_col] and
                  data[i-1, close_col] > data[i-1, open_col] and
                  data[i, close_col] > data[i, upper_band]):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### Strategy 3: Piercing + Stochastic Oscillator

**Concept:** Combine Piercing/Dark Cloud pattern with Stochastic at extremes.

**Conditions:**

- **Long:** Bullish Piercing + Stochastic(14) < 20
- **Short:** Bearish Piercing + Stochastic(14) > 80

```python
lower_barrier = 20
upper_barrier = 80

def signal(data, open_col, close_col, stoch_col, buy_col, sell_col):
    data = add_column(data, 5)
    for i in range(len(data)):
        try:
            # Bullish Piercing at oversold
            if (data[i, close_col] > data[i, open_col] and
                data[i, close_col] < data[i-1, open_col] and
                data[i, close_col] > data[i-1, close_col] and
                data[i, open_col] < data[i-1, close_col] and
                data[i-1, close_col] < data[i-1, open_col] and
                data[i, stoch_col] < lower_barrier):
                data[i + 1, buy_col] = 1
            # Bearish Piercing at overbought
            elif (data[i, close_col] < data[i, open_col] and
                  data[i, close_col] > data[i-1, open_col] and
                  data[i, close_col] < data[i-1, close_col] and
                  data[i, open_col] > data[i-1, close_col] and
                  data[i-1, close_col] > data[i-1, open_col] and
                  data[i, stoch_col] > upper_barrier):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### Strategy 4: Euphoria + K's Envelopes

**Concept:** Trade Euphoria (exhaustion) patterns when price is inside the K's Envelopes support/resistance zone.

**Conditions:**

- **Long:** Bullish Euphoria + Close inside K's Envelopes
- **Short:** Bearish Euphoria + Close inside K's Envelopes

```python
def signal(data, open_col, close_col, upper_envelope, lower_envelope, buy_col, sell_col):
    data = add_column(data, 5)
    data = rounding(data, 4)
    for i in range(len(data)):
        try:
            # Bullish Euphoria inside envelopes
            if (data[i, open_col] > data[i, close_col] and
                data[i-1, open_col] > data[i-1, close_col] and
                data[i-2, open_col] > data[i-2, close_col] and
                data[i, close_col] < data[i-1, close_col] and
                data[i-1, close_col] < data[i-2, close_col] and
                (data[i, open_col] - data[i, close_col]) > (data[i-1, open_col] - data[i-1, close_col]) and
                (data[i-1, open_col] - data[i-1, close_col]) > (data[i-2, open_col] - data[i-2, close_col]) and
                data[i, close_col] > data[i, lower_envelope] and
                data[i, close_col] < data[i, upper_envelope]):
                data[i + 1, buy_col] = 1
            # Bearish Euphoria inside envelopes
            elif (data[i, open_col] < data[i, close_col] and
                  data[i-1, open_col] < data[i-1, close_col] and
                  data[i-2, open_col] < data[i-2, close_col] and
                  data[i, close_col] > data[i-1, close_col] and
                  data[i-1, close_col] > data[i-2, close_col] and
                  (data[i, close_col] - data[i, open_col]) > (data[i-1, close_col] - data[i-1, open_col]) and
                  (data[i-1, close_col] - data[i-1, open_col]) > (data[i-2, close_col] - data[i-2, open_col]) and
                  data[i, close_col] > data[i, lower_envelope] and
                  data[i, close_col] < data[i, upper_envelope]):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

### Strategy 5: Barrier + RSI-ATR

**Concept:** Combine the Barrier pattern (support/resistance) with the volatility-weighted RSI-ATR indicator.

**RSI-ATR Formula:** RSI calculated on (RSI / ATR) — more reactive than standard RSI.

**Conditions:**

- **Long:** Bullish Barrier + RSI-ATR(5) < 20
- **Short:** Bearish Barrier + RSI-ATR(5) > 80

```python
def rsi_atr(data, lookback_rsi, lookback_atr, lookback_rsi_atr, high, low, close, position):
    """Calculate RSI-ATR: RSI of (RSI / ATR)"""
    data = rsi(data, lookback_rsi, close, position)
    data = atr(data, lookback_atr, high, low, close, position + 1)
    data = add_column(data, 1)
    data[:, position + 2] = data[:, position] / data[:, position + 1]
    data = rsi(data, lookback_rsi_atr, position + 2, position + 3)
    data = delete_column(data, position, 3)
    return data

# Signal function
lower_barrier = 20
upper_barrier = 80

def signal(data, open_col, close_col, rsi_atr_col, buy_col, sell_col):
    data = add_column(data, 5)
    for i in range(len(data)):
        try:
            # Bullish Barrier at oversold RSI-ATR
            if (data[i, close_col] > data[i, open_col] and
                data[i-1, close_col] < data[i-1, open_col] and
                data[i-2, close_col] < data[i-2, open_col] and
                # Same lows (Barrier condition - requires rounding)
                data[i, rsi_atr_col] < lower_barrier):
                data[i + 1, buy_col] = 1
            # Bearish Barrier at overbought RSI-ATR
            elif (data[i, close_col] < data[i, open_col] and
                  data[i-1, close_col] > data[i-1, open_col] and
                  data[i-2, close_col] > data[i-2, open_col] and
                  # Same highs (Barrier condition - requires rounding)
                  data[i, rsi_atr_col] > upper_barrier):
                data[i + 1, sell_col] = -1
        except IndexError:
            pass
    return data
```

---

## Exit Techniques (Chapter 9)

When trading candlestick patterns, three key decisions must be made: entry, target (profit-taking), and stop (loss-limiting). Chapter 9 focuses on exit strategies.

### The Symmetrical Exit Technique

Projects a target based on the key candlestick's range (high - low), measured from the pattern's extremity.

**Bullish Target:** High + (High - Low)  
**Bearish Target:** Low - (High - Low)

```python
# Bullish symmetrical target
target = key_candle_high + (key_candle_high - key_candle_low)

# Bearish symmetrical target
target = key_candle_low - (key_candle_high - key_candle_low)
```

### The Fixed Holding Period Exit

Exit after a predetermined number of time periods regardless of price. Simple but inflexible.

```python
holding_period = 5  # Exit after 5 candles
```

### The Variable Holding Period Exit

Exit only when another pattern appears (bullish or bearish). Used in the book's backtests. Risk: positions can remain open too long with rare patterns.

### The Hybrid Exit Technique (Recommended)

Combines all three methods with weighted allocation:

1. **Symmetrical projection** - Given weight (e.g., 50%)
2. **Variable holding period** - Remainder weight (e.g., 50%)
3. **Fixed holding period** - Maximum duration safety net

Exit whichever condition triggers first, closing the weighted portion.

### Pattern Invalidation (Stop-Loss)

**Fixed Stop-Loss:** Set fixed pip/point distance (not recommended - ignores volatility)

**ATR-Based Stop-Loss (Recommended):** Dynamic stop based on Average True Range

```python
# ATR-based stop-loss
atr_multiplier = 2
stop_loss = entry_price - (atr_value * atr_multiplier)  # For long positions
```

| Exit Technique   | Duration     | Based On         |
| ---------------- | ------------ | ---------------- |
| Symmetrical      | Medium-Long  | Price            |
| Fixed Holding    | User-defined | Time             |
| Variable Holding | Medium-Long  | Price (patterns) |
| Hybrid           | Medium-Long  | Price + Time     |

---

## Alternative Charting Systems (Chapter 8)

These alternative candlestick charting systems transform OHLC data to provide smoother, trend-focused views. Patterns can be detected on these transformed charts for a different perspective.

### Heikin-Ashi System

**Summary:** "Heikin-Ashi" means "average bar" in Japanese. This system transforms OHLC data using averaging formulas to create smoothed candlesticks that better reveal underlying trends. Color alternation is less common, making trends easier to identify. The transformed values are not real prices.

**Formulas:**

- **HA Open** = (Previous Open + Previous Close) / 2
- **HA Close** = (Open + High + Low + Close) / 4
- **HA High** = Maximum of (High, HA Open, HA Close)
- **HA Low** = Minimum of (Low, HA Open, HA Close)

**Advantages:**

- Better trend visibility due to color clustering
- Noise reduction through smoothing
- Easier trend interpretation

**Limitations:**

- Values are not real prices
- Small lag in detecting reversals
- Alternating colors in flat/ranging markets

```python
def heikin_ashi(data, open_col, high_col, low_col, close_col, position):
    """
    Transform OHLC data into Heikin-Ashi candlesticks.
    Results stored in columns starting at 'position'.
    """
    data = add_column(data, 4)

    # Heikin-Ashi Open = (previous open + previous close) / 2
    try:
        for i in range(len(data)):
            data[i, position] = (data[i-1, open_col] + data[i-1, close_col]) / 2
    except:
        pass

    # Heikin-Ashi Close = (open + high + low + close) / 4
    for i in range(len(data)):
        data[i, position + 3] = (data[i, open_col] + data[i, high_col] +
                                  data[i, low_col] + data[i, close_col]) / 4

    # Heikin-Ashi High = max(high, HA open, HA close)
    for i in range(len(data)):
        data[i, position + 1] = max(data[i, position],
                                     data[i, position + 3],
                                     data[i, high_col])

    # Heikin-Ashi Low = min(low, HA open, HA close)
    for i in range(len(data)):
        data[i, position + 2] = min(data[i, position],
                                     data[i, position + 3],
                                     data[i, low_col])

    return data
```

**Usage with Patterns:**
After transforming data to Heikin-Ashi, apply the same pattern detection functions using the new HA column indices. Performance should be measured against real OHLC prices, not transformed values.

---

### K's Candlesticks System

**Summary:** K's Candlesticks provide even smoother trend visualization than Heikin-Ashi by applying a simple moving average (default period: 3) to each OHLC component independently. This creates highly smoothed candlesticks with greater lag but clearer trend direction.

**Formulas (with lookback = 3):**

- **K's Open** = (Open[i] + Open[i-1] + Open[i-2]) / 3
- **K's High** = (High[i] + High[i-1] + High[i-2]) / 3
- **K's Low** = (Low[i] + Low[i-1] + Low[i-2]) / 3
- **K's Close** = (Close[i] + Close[i-1] + Close[i-2]) / 3

**Advantages:**

- Even smoother than Heikin-Ashi (lookback of 3 vs 1)
- Very clear trend visualization
- Excellent for filtering noise

**Limitations:**

- Larger lag than Heikin-Ashi
- Values are not real prices
- Can miss quick reversals due to smoothing

```python
def k_candlesticks(data, open_col, high_col, low_col, close_col, lookback, position):
    """
    Transform OHLC data into K's Candlesticks using simple moving averages.
    Default lookback is 3 periods.
    Results stored in columns starting at 'position'.
    """
    data = add_column(data, 4)

    # K's Open = SMA of Open prices
    data = ma(data, lookback, open_col, position)

    # K's High = SMA of High prices
    data = ma(data, lookback, high_col, position + 1)

    # K's Low = SMA of Low prices
    data = ma(data, lookback, low_col, position + 2)

    # K's Close = SMA of Close prices
    data = ma(data, lookback, close_col, position + 3)

    return data


def ma(data, lookback, source_col, result_col):
    """
    Calculate Simple Moving Average.
    """
    for i in range(lookback, len(data)):
        data[i, result_col] = sum(data[i-lookback+1:i+1, source_col]) / lookback
    return data
```

**Usage with Patterns:**

```python
# Transform data to K's candlesticks (lookback=3, store starting at column 4)
my_data = k_candlesticks(my_data, 0, 1, 2, 3, 3, 4)

# Apply pattern detection on K's columns (4, 5, 6, 7)
# Measure performance using real OHLC (columns 0-3)
```

---

### Comparison of Charting Systems

| System               | Smoothing | Lag    | Best For                         |
| -------------------- | --------- | ------ | -------------------------------- |
| Regular Candlesticks | None      | None   | Real prices, precise entries     |
| Heikin-Ashi          | Moderate  | Small  | Trend identification             |
| K's Candlesticks     | High      | Larger | Clear trend direction, filtering |

**Best Practice:** Use multiple charting systems together:

1. Detect patterns on alternative charts for diversification
2. Always measure performance against real OHLC data
3. Consider the lag when timing entries/exits

---

## Helper Functions

All patterns require these helper functions:

```python
import numpy as np

def add_column(data, times):
    """Add empty columns to the data array"""
    for i in range(1, times + 1):
        new = np.zeros((len(data), 1), dtype=float)
        data = np.append(data, new, axis=1)
    return data

def rounding(data, decimals):
    """Round all values in the array to specified decimal places"""
    data = data.round(decimals=decimals)
    return data
```

---

## Column Index Reference

Standard OHLC array indexing used throughout:

- **Index 0**: Open price
- **Index 1**: High price
- **Index 2**: Low price
- **Index 3**: Close price
- **Index 4**: Buy signals (1 = buy)
- **Index 5**: Sell signals (-1 = sell)

---

## Notes on Usage

1. **Rounding**: For patterns requiring exact price matches (Doji, On Neck, Tweezers), round OHLC data to 4 decimal places for currencies.

2. **Body/Wick Parameters**: Adjust the `body` and `wick` threshold parameters based on the asset's typical volatility and price scale.

3. **Confirmation**: Most contrarian patterns require prior trend confirmation (checking candles before the pattern).

4. **Signal Timing**: Signals are placed on `data[i + 1]` to execute on the next candle's open after pattern completion.

---

_Reference: Mastering Financial Pattern Recognition by Sofien Kaabar (O'Reilly, 2023)_
