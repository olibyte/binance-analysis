# Setup Instructions

## Step 1: Create Virtual Environment

```bash
python3 -m venv venv
```

## Step 2: Activate Virtual Environment

**On macOS/Linux:**

```bash
source venv/bin/activate
```

**On Windows:**

```bash
venv\Scripts\activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Launch Jupyter Notebook

```bash
jupyter notebook
```

Or if you prefer JupyterLab:

```bash
jupyter lab
```

## Step 5: Open the Notebook

Navigate to and open `binance_analysis.ipynb` in Jupyter.

## Usage

1. Run all cells sequentially to fetch and process Binance klines data
2. The notebook will fetch BTCUSDT 1-hour klines data by default
3. You can modify `SYMBOL` and `INTERVAL` variables in cell 1 to fetch different data
4. The DataFrame `df` will contain the processed OHLCV data ready for technical indicator calculations

## Notes

- Binance API returns data in UTC timezone
- Default limit is 500 klines (maximum is 1000)
- The notebook uses BTCUSDT (not BTCUSD) as Binance uses USDT pairs

