import requests
from tradingview_ta import TA_Handler, Interval, Exchange
import urllib3
import pandas as pd
import json
from datetime import datetime
import os
import time

# Disable SSL warnings when verification is disabled
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Monkey patch requests.Session to disable SSL verification for tradingview_ta
# This is needed because tradingview_ta doesn't expose SSL verification options
# and macOS often has SSL certificate issues
_original_request = requests.Session.request

def _patched_request(self, method, url, **kwargs):
    # Disable SSL verification for tradingview.com requests to avoid certificate errors
    if 'scanner.tradingview.com' in url or 'tradingview.com' in url:
        kwargs['verify'] = False
    return _original_request(self, method, url, **kwargs)

requests.Session.request = _patched_request

# Cache for signals to avoid redundant API calls
_signals_cache = {'data': None, 'timestamp': None}


def _get_analysis_with_retry(handler, max_retries=3, base_delay=2, print_output=True):
    """
    Get analysis from TradingView API with retry logic and exponential backoff for 429 errors.
    
    Parameters:
    -----------
    handler : TA_Handler
        TradingView TA handler instance
    max_retries : int, optional
        Maximum number of retry attempts (default: 3)
    base_delay : float, optional
        Base delay in seconds for exponential backoff (default: 2)
    print_output : bool, optional
        If True, print retry messages (default: True)
    
    Returns:
    --------
    Analysis object from handler.get_analysis()
    
    Raises:
    -------
    Exception
        If all retries are exhausted
    """
    for attempt in range(max_retries):
        try:
            return handler.get_analysis()
        except Exception as e:
            error_msg = str(e)
            # Check if it's a 429 rate limit error
            is_rate_limit = '429' in error_msg or 'rate limit' in error_msg.lower()
            
            if is_rate_limit and attempt < max_retries - 1:
                # Calculate exponential backoff delay
                delay = base_delay * (2 ** attempt)
                if print_output:
                    print(f"  Rate limit hit (429). Retrying in {delay:.1f} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
            else:
                # Not a rate limit error, or we've exhausted retries
                raise


def get_btcusd_signals(save=False, print_output=True, delay_between_requests=1.5, 
                       use_cache=True, cache_ttl=30, max_retries=3, base_delay=2):
    """
    Get BTCUSD trading signals from TradingView across multiple timeframes.
    
    Parameters:
    -----------
    save : bool, optional
        If True, automatically save signals to CSV and JSON files (default: False)
    print_output : bool, optional
        If True, print the signal table to console (default: True)
    delay_between_requests : float, optional
        Time in seconds to wait between API requests (default: 1.5)
    use_cache : bool, optional
        If True, use cached results if available and within TTL (default: True)
    cache_ttl : int, optional
        Cache time-to-live in seconds (default: 30)
    max_retries : int, optional
        Maximum retry attempts for 429 rate limit errors (default: 3)
    base_delay : float, optional
        Base delay in seconds for exponential backoff on retries (default: 2)
    
    Returns:
    --------
    list
        List of dictionaries, each containing:
        - timestamp: ISO format timestamp when signal was captured
        - timeframe: Timeframe label (e.g., "1 Minute", "5 Minutes")
        - signal: Signal type (e.g., "BUY", "SELL", "NEUTRAL", "STRONG_BUY")
        - buy: Number of buy indicators
        - sell: Number of sell indicators
        - neutral: Number of neutral indicators
    """
    # Check cache if enabled
    global _signals_cache
    current_time = time.time()
    
    if use_cache and _signals_cache['data'] is not None and _signals_cache['timestamp'] is not None:
        cache_age = current_time - _signals_cache['timestamp']
        if cache_age < cache_ttl:
            if print_output:
                print(f"Using cached signals (age: {cache_age:.1f}s, TTL: {cache_ttl}s)")
            return _signals_cache['data']
    
    # Map readable labels to tradingview_ta Interval constants
    timeframes = {
        "1 Minute": Interval.INTERVAL_1_MINUTE,
        "5 Minutes": Interval.INTERVAL_5_MINUTES,
        "15 Minutes": Interval.INTERVAL_15_MINUTES,
        "30 Minutes": Interval.INTERVAL_30_MINUTES,
        "1 Hour": Interval.INTERVAL_1_HOUR,
        "2 Hour": Interval.INTERVAL_2_HOURS,
        "4 Hour": Interval.INTERVAL_4_HOURS,
        "1 Day": Interval.INTERVAL_1_DAY,
        "1 Week": Interval. INTERVAL_1_WEEK
    }

    # Get current timestamp
    timestamp = datetime.now().isoformat()
    
    # Store signals
    signals = []

    # Print a table header if requested
    if print_output:
        print(f"{'Timeframe':<12} | {'Signal':<15} | {'Details (Buy/Sell/Neut)'}")
        print("-" * 55)

    for idx, (label, interval_const) in enumerate(timeframes.items()):
        # Add delay between requests (except before the first one)
        if idx > 0 and delay_between_requests > 0:
            time.sleep(delay_between_requests)
        
        try:
            handler = TA_Handler(
                symbol="BTCUSD",
                screener="crypto",
                exchange="COINBASE", 
                interval=interval_const
            )
            
            # Use retry helper for API call
            analysis = _get_analysis_with_retry(handler, max_retries=max_retries, 
                                               base_delay=base_delay, print_output=print_output)
            summary = analysis.summary
            
            signal = summary['RECOMMENDATION']
            buy = summary['BUY']
            sell = summary['SELL']
            neutral = summary['NEUTRAL']
            
            # Store signal data
            signal_data = {
                'timestamp': timestamp,
                'timeframe': label,
                'signal': signal,
                'buy': buy,
                'sell': sell,
                'neutral': neutral
            }
            signals.append(signal_data)
            
            # Format the output row if requested
            if print_output:
                print(f"{label:<12} | {signal:<15} | {buy}B / {sell}S / {neutral}N")

        except Exception as e:
            error_msg = str(e)
            # Store error signal
            signal_data = {
                'timestamp': timestamp,
                'timeframe': label,
                'signal': 'ERROR',
                'buy': None,
                'sell': None,
                'neutral': None,
                'error': error_msg
            }
            signals.append(signal_data)
            
            if print_output:
                print(f"{label:<12} | {'ERROR':<15} | {error_msg}")
    
    # Update cache if enabled
    if use_cache:
        _signals_cache['data'] = signals
        _signals_cache['timestamp'] = time.time()
    
    # Auto-save if requested
    if save:
        save_signals(signals)
    
    return signals


def save_signals(signals, filename=None):
    """
    Save signals to both CSV and JSON files.
    
    Parameters:
    -----------
    signals : list
        List of signal dictionaries to save
    filename : str, optional
        Base filename (without extension). If None, uses 'btcusd_signals_history'
    
    Returns:
    --------
    tuple
        (csv_path, json_path) paths where files were saved
    """
    if filename is None:
        filename = 'btcusd_signals_history'
    
    csv_path = f"{filename}.csv"
    json_path = f"{filename}.json"
    
    # Convert to DataFrame for CSV
    df = pd.DataFrame(signals)
    
    # Append to CSV if file exists, otherwise create new
    if os.path.exists(csv_path):
        existing_df = pd.read_csv(csv_path)
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        combined_df.to_csv(csv_path, index=False)
    else:
        df.to_csv(csv_path, index=False)
    
    # Append to JSON if file exists, otherwise create new
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            existing_data = json.load(f)
        existing_data.extend(signals)
        with open(json_path, 'w') as f:
            json.dump(existing_data, f, indent=2)
    else:
        with open(json_path, 'w') as f:
            json.dump(signals, f, indent=2)
    
    return csv_path, json_path


def load_signals_history(filename=None):
    """
    Load historical signals from CSV or JSON file.
    
    Parameters:
    -----------
    filename : str, optional
        Base filename (without extension). If None, uses 'btcusd_signals_history'
        Will try CSV first, then JSON if CSV doesn't exist
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame containing all historical signals, or empty DataFrame if file doesn't exist
    """
    if filename is None:
        filename = 'btcusd_signals_history'
    
    csv_path = f"{filename}.csv"
    json_path = f"{filename}.json"
    
    # Try CSV first (preferred format)
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            # Convert timestamp to datetime if it exists
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        except Exception as e:
            print(f"Error loading CSV file: {e}")
    
    # Fallback to JSON
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
            # Convert timestamp to datetime if it exists
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        except Exception as e:
            print(f"Error loading JSON file: {e}")
    
    # Return empty DataFrame if no file exists
    return pd.DataFrame()


def get_signals_history(filename=None):
    """
    Convenience function to get DataFrame of all historical signals.
    Alias for load_signals_history().
    
    Parameters:
    -----------
    filename : str, optional
        Base filename (without extension). If None, uses 'btcusd_signals_history'
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame containing all historical signals, or empty DataFrame if file doesn't exist
    """
    return load_signals_history(filename)


# Binance API Configuration
BASE_URL = "https://api.binance.com/api/v3/klines"


def _interval_to_milliseconds(interval):
    """
    Convert Binance interval string to milliseconds.
    
    Parameters:
    -----------
    interval : str
        Interval string (e.g., '1m', '5m', '15m', '1h', '1d')
    
    Returns:
    --------
    int
        Interval duration in milliseconds
    """
    interval_map = {
        '1m': 60 * 1000,
        '3m': 3 * 60 * 1000,
        '5m': 5 * 60 * 1000,
        '15m': 15 * 60 * 1000,
        '30m': 30 * 60 * 1000,
        '1h': 60 * 60 * 1000,
        '2h': 2 * 60 * 60 * 1000,
        '4h': 4 * 60 * 60 * 1000,
        '6h': 6 * 60 * 60 * 1000,
        '8h': 8 * 60 * 60 * 1000,
        '12h': 12 * 60 * 60 * 1000,
        '1d': 24 * 60 * 60 * 1000,
        '3d': 3 * 24 * 60 * 60 * 1000,
        '1w': 7 * 24 * 60 * 60 * 1000,
        '1M': 30 * 24 * 60 * 60 * 1000,  # Approximate month
    }
    
    if interval not in interval_map:
        raise ValueError(f"Unsupported interval: {interval}. Supported intervals: {list(interval_map.keys())}")
    
    return interval_map[interval]


def _datetime_to_timestamp_ms(dt):
    """
    Convert datetime object, timestamp (seconds or milliseconds), or None to milliseconds timestamp.
    
    Parameters:
    -----------
    dt : datetime, int, float, or None
        Datetime object, Unix timestamp (seconds or milliseconds), or None
    
    Returns:
    --------
    int or None
        Timestamp in milliseconds, or None if dt is None
    """
    if dt is None:
        return None
    
    if isinstance(dt, datetime):
        return int(dt.timestamp() * 1000)
    elif isinstance(dt, (int, float)):
        # If timestamp is less than year 2000 in seconds, assume it's in seconds
        # Otherwise assume milliseconds
        if dt < 946684800000:  # Year 2000 in milliseconds
            return int(dt * 1000)
        else:
            return int(dt)
    else:
        raise TypeError(f"Unsupported type for datetime conversion: {type(dt)}")


def _calculate_chunk_end_time(start_time_ms, interval, num_candles):
    """
    Calculate end time for a chunk given start time, interval, and number of candles.
    
    Parameters:
    -----------
    start_time_ms : int
        Start time in milliseconds
    interval : str
        Interval string (e.g., '1h', '15m')
    num_candles : int
        Number of candles in the chunk
    
    Returns:
    --------
    int
        End time in milliseconds (exclusive, i.e., start of next candle)
    """
    interval_ms = _interval_to_milliseconds(interval)
    return start_time_ms + (num_candles * interval_ms)


def _fetch_klines_with_retry(symbol, interval, limit=1000, start_time=None, end_time=None, 
                              verify_ssl=True, max_retries=3, base_delay=2):
    """
    Internal function to fetch klines with retry logic for rate limiting.
    
    Parameters:
    -----------
    symbol : str
        Trading pair symbol (e.g., 'BTCUSDT')
    interval : str
        Kline interval (e.g., '1h', '4h', '1d')
    limit : int
        Number of klines to retrieve (default: 1000, max: 1000)
    start_time : int, optional
        Start time in milliseconds (Unix timestamp)
    end_time : int, optional
        End time in milliseconds (Unix timestamp)
    verify_ssl : bool
        Whether to verify SSL certificates (default: True)
    max_retries : int
        Maximum number of retry attempts (default: 3)
    base_delay : float
        Base delay in seconds for exponential backoff (default: 2)
    
    Returns:
    --------
    list or None
        List of kline arrays from Binance API, or None if all retries fail
    """
    params = {
        'symbol': symbol,
        'interval': interval,
        'limit': limit
    }
    
    if start_time is not None:
        params['startTime'] = start_time
    if end_time is not None:
        params['endTime'] = end_time
    
    for attempt in range(max_retries):
        try:
            # Try with SSL verification first
            response = requests.get(BASE_URL, params=params, verify=verify_ssl, timeout=10)
            
            # Check for rate limit (429)
            if response.status_code == 429:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    print(f"Rate limit hit (429). Retrying in {delay:.1f} seconds... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                    continue
                else:
                    response.raise_for_status()
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.SSLError as e:
            if verify_ssl and attempt == 0:
                # If SSL verification failed and it was enabled, try without it
                print("SSL certificate verification failed. Retrying without verification...")
                print("Note: For production, install certificates properly using: pip install --upgrade certifi")
                verify_ssl = False
                continue
            else:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                else:
                    print(f"SSL Error: {e}")
                    return None
                    
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                print(f"Error fetching data: {e}. Retrying in {delay:.1f} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
                continue
            else:
                print(f"Error fetching data (all retries exhausted): {e}")
                return None
    
    return None


def fetch_klines(symbol, interval, limit=1000, start_time=None, end_time=None, verify_ssl=True):
    """
    Fetch klines (candlestick) data from Binance API.
    
    Parameters:
    -----------
    symbol : str
        Trading pair symbol (e.g., 'BTCUSDT')
    interval : str
        Kline interval (e.g., '1h', '4h', '1d')
    limit : int
        Number of klines to retrieve (default: 1000, max: 1000)
    start_time : datetime, int, float, or None, optional
        Start time for data retrieval. Can be:
        - datetime object
        - Unix timestamp in seconds (int/float)
        - Unix timestamp in milliseconds (int/float, must be > year 2000 in ms)
        - None (default: most recent data)
    end_time : datetime, int, float, or None, optional
        End time for data retrieval. Same format as start_time.
        - None (default: current time)
    verify_ssl : bool
        Whether to verify SSL certificates (default: True)
        Set to False if experiencing SSL certificate errors
    
    Returns:
    --------
    list
        List of kline arrays from Binance API, or None on error
    """
    # Convert start_time and end_time to milliseconds if provided
    start_time_ms = _datetime_to_timestamp_ms(start_time) if start_time is not None else None
    end_time_ms = _datetime_to_timestamp_ms(end_time) if end_time is not None else None
    
    return _fetch_klines_with_retry(
        symbol=symbol,
        interval=interval,
        limit=limit,
        start_time=start_time_ms,
        end_time=end_time_ms,
        verify_ssl=verify_ssl
    )


def fetch_historical_klines(symbol, interval, start_time, end_time=None, 
                            max_candles_per_request=1000, rate_limit_delay=0.05,
                            verify_ssl=True, progress_callback=None, max_retries=3):
    """
    Fetch large amounts of historical klines data by paginating through time ranges.
    
    This function automatically handles pagination, rate limiting, and data merging
    to collect historical data beyond the 1000-candle limit per request.
    
    Parameters:
    -----------
    symbol : str
        Trading pair symbol (e.g., 'BTCUSDT')
    interval : str
        Kline interval (e.g., '1h', '15m', '1d')
    start_time : datetime, int, or float
        Start time for data retrieval. Can be:
        - datetime object
        - Unix timestamp in seconds (int/float)
        - Unix timestamp in milliseconds (int/float, must be > year 2000 in ms)
    end_time : datetime, int, float, or None, optional
        End time for data retrieval. Same format as start_time.
        - None (default: current time)
    max_candles_per_request : int, optional
        Maximum candles per API request (default: 1000, Binance maximum)
    rate_limit_delay : float, optional
        Delay in seconds between API requests to respect rate limits
        (default: 0.05 = 20 req/sec, well under 1200 req/min limit)
    verify_ssl : bool, optional
        Whether to verify SSL certificates (default: True)
    progress_callback : callable, optional
        Optional callback function called after each chunk is fetched.
        Signature: callback(current_chunk, total_chunks, candles_fetched)
    max_retries : int, optional
        Maximum retry attempts for failed requests (default: 3)
    
    Returns:
    --------
    list
        List of kline arrays from Binance API, sorted chronologically by open_time.
        Returns empty list if no data is available or on error.
    
    Examples:
    ---------
    >>> from datetime import datetime, timedelta
    >>> from data import fetch_historical_klines
    >>> 
    >>> # Fetch last 6 months of hourly data
    >>> end_time = datetime.now()
    >>> start_time = end_time - timedelta(days=180)
    >>> klines = fetch_historical_klines('BTCUSDT', '1h', start_time, end_time)
    >>> print(f"Fetched {len(klines)} candles")
    """
    # Convert times to milliseconds
    start_time_ms = _datetime_to_timestamp_ms(start_time)
    if end_time is None:
        end_time_ms = int(time.time() * 1000)  # Current time in milliseconds
    else:
        end_time_ms = _datetime_to_timestamp_ms(end_time)
    
    # Validate time range
    if start_time_ms >= end_time_ms:
        print(f"Error: start_time ({start_time_ms}) must be before end_time ({end_time_ms})")
        return []
    
    # Calculate interval duration in milliseconds
    interval_ms = _interval_to_milliseconds(interval)
    
    # Calculate total time span and estimate number of candles
    total_time_ms = end_time_ms - start_time_ms
    estimated_candles = total_time_ms // interval_ms
    
    # Calculate number of chunks needed
    num_chunks = (estimated_candles + max_candles_per_request - 1) // max_candles_per_request
    
    if num_chunks == 0:
        num_chunks = 1  # At least one request
    
    print(f"Fetching historical data: {estimated_candles} estimated candles in {num_chunks} chunk(s)")
    
    all_klines = []
    current_end = end_time_ms
    
    # Fetch chunks in reverse chronological order (newest to oldest)
    # This ensures we get the most recent data first
    for chunk_num in range(num_chunks):
        # Calculate chunk start time
        # Each chunk covers max_candles_per_request candles
        chunk_duration_ms = max_candles_per_request * interval_ms
        chunk_start = max(start_time_ms, current_end - chunk_duration_ms)
        
        # Fetch this chunk
        chunk_klines = _fetch_klines_with_retry(
            symbol=symbol,
            interval=interval,
            limit=max_candles_per_request,
            start_time=chunk_start,
            end_time=current_end,
            verify_ssl=verify_ssl,
            max_retries=max_retries
        )
        
        if chunk_klines is None:
            print(f"Warning: Failed to fetch chunk {chunk_num + 1}/{num_chunks}")
            # Move to next chunk anyway
            current_end = chunk_start
            continue
        
        if len(chunk_klines) == 0:
            # No more data available
            break
        
        # Add to collection (will reverse later)
        all_klines.extend(chunk_klines)
        
        # Update progress callback if provided
        if progress_callback:
            try:
                progress_callback(chunk_num + 1, num_chunks, len(all_klines))
            except Exception as e:
                print(f"Warning: Progress callback error: {e}")
        
        # Update current_end for next chunk (exclusive, so use first candle's open_time)
        if len(chunk_klines) > 0:
            first_candle_time = int(chunk_klines[0][0])  # First element is open_time
            current_end = first_candle_time
        
        # Check if we've reached the start time
        if current_end <= start_time_ms:
            break
        
        # Rate limiting: delay between requests
        if chunk_num < num_chunks - 1:  # Don't delay after last chunk
            time.sleep(rate_limit_delay)
    
    if len(all_klines) == 0:
        print("No data retrieved")
        return []
    
    # Remove duplicates based on open_time (first element of each kline array)
    seen_times = set()
    unique_klines = []
    for kline in all_klines:
        open_time = int(kline[0])
        if open_time not in seen_times:
            seen_times.add(open_time)
            unique_klines.append(kline)
    
    # Sort by open_time (first element) chronologically
    unique_klines.sort(key=lambda x: int(x[0]))
    
    # Filter to ensure all candles are within requested time range
    filtered_klines = [
        kline for kline in unique_klines
        if start_time_ms <= int(kline[0]) < end_time_ms
    ]
    
    print(f"Successfully fetched {len(filtered_klines)} unique candles")
    
    # Check for gaps (optional validation)
    if len(filtered_klines) > 1:
        gaps = []
        for i in range(len(filtered_klines) - 1):
            current_time = int(filtered_klines[i][0])
            next_time = int(filtered_klines[i + 1][0])
            expected_next = current_time + interval_ms
            if next_time != expected_next:
                gaps.append((current_time, next_time, expected_next))
        
        if gaps:
            print(f"Warning: Found {len(gaps)} gap(s) in data (missing candles)")
    
    return filtered_klines
