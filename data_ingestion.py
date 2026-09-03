"""
Data Ingestion Pipeline fetching stock market OHLCV data via yfinance and populating MongoDB.
Includes manual sample record seeding for student testing and experimentation.
"""
import os
import time
import logging
from datetime import datetime
import pandas as pd
import numpy as np
import yfinance as yf
import config
from database import db_manager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Student sample manual test ticks inserted for testing single-day tick ingestion
SAMPLE_STUDENT_TEST_TICKS = [
    {"ticker": "AAPL", "date": datetime(2025, 1, 15), "open": 185.50, "high": 188.20, "low": 184.90, "close": 187.80, "volume": 48291000, "daily_return": 1.2399, "sma_30": 184.20, "volatility_30": 1.05},
    {"ticker": "MSFT", "date": datetime(2025, 1, 15), "open": 390.10, "high": 395.40, "low": 389.50, "close": 394.20, "volume": 22104000, "daily_return": 1.0510, "sma_30": 388.90, "volatility_30": 0.95},
    {"ticker": "NVDA", "date": datetime(2025, 1, 15), "open": 125.40, "high": 131.80, "low": 124.90, "close": 130.50, "volume": 65420000, "daily_return": 4.0669, "sma_30": 122.10, "volatility_30": 2.45},
    {"ticker": "TSLA", "date": datetime(2025, 1, 15), "open": 240.20, "high": 252.10, "low": 238.50, "close": 249.90, "volume": 58310000, "daily_return": 4.0383, "sma_30": 235.40, "volatility_30": 3.10}
]

def insert_manual_test_records():
    """Inserts student sample test records into MongoDB for verification."""
    col = db_manager.get_collection()
    for tick in SAMPLE_STUDENT_TEST_TICKS:
        try:
            col.update_one(
                {"ticker": tick["ticker"], "date": tick["date"]},
                {"$set": tick},
                upsert=True
            )
        except Exception as e:
            logger.warning(f"Test record insert notice: {e}")
    logger.info("Sample test records inserted successfully for student verification.")

def fetch_stock_data(tickers=config.TICKERS, start_date=config.START_DATE, end_date=config.END_DATE):
    """Fetches historical daily OHLCV data for multiple stock tickers using yfinance."""
    logger.info(f"Fetching data for {len(tickers)} tickers from {start_date} to {end_date}...")
    
    # Try loading from local CSV backup if exists to save time
    backup_file = os.path.join(config.DATA_DIR, "stock_data_backup.csv")
    if os.path.exists(backup_file):
        logger.info(f"Loading stock data from local backup file: {backup_file}")
        df = pd.read_csv(backup_file)
        df['date'] = pd.to_datetime(df['date'])
        return df

    all_data = []
    
    # Fetch in batches of 20
    batch_size = 20
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i + batch_size]
        logger.info(f"Downloading batch {i // batch_size + 1}/{(len(tickers) + batch_size - 1) // batch_size}: {batch}")
        try:
            download_df = yf.download(
                tickers=batch,
                start=start_date,
                end=end_date,
                group_by='ticker',
                auto_adjust=False,
                threads=True,
                progress=False
            )
            
            for ticker in batch:
                try:
                    if len(batch) == 1:
                        ticker_df = download_df.copy()
                    else:
                        if ticker in download_df.columns.levels[0]:
                            ticker_df = download_df[ticker].copy()
                        else:
                            continue
                            
                    ticker_df = ticker_df.dropna(how='all')
                    if ticker_df.empty:
                        continue
                        
                    ticker_df = ticker_df.reset_index()

                    # Standardize column names
                    col_map = {'Date': 'date', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'}
                    ticker_df = ticker_df.rename(columns=col_map)
                    
                    if 'date' not in ticker_df.columns or 'close' not in ticker_df.columns:
                        continue

                    # Required numeric columns
                    for col in ['open', 'high', 'low', 'close', 'volume']:
                        if col in ticker_df.columns:
                            ticker_df[col] = pd.to_numeric(ticker_df[col], errors='coerce')
                            
                    ticker_df = ticker_df.dropna(subset=['close', 'open'])
                    if ticker_df.empty:
                        continue
                        
                    ticker_df['ticker'] = ticker
                    
                    # Calculate Daily Return (%)
                    ticker_df['daily_return'] = ((ticker_df['close'] - ticker_df['open']) / ticker_df['open']) * 100.0
                    
                    # Calculate 30-day Moving Average (SMA_30) and 30-day Volatility
                    ticker_df['sma_30'] = ticker_df['close'].rolling(window=30, min_periods=1).mean()
                    ticker_df['volatility_30'] = ticker_df['daily_return'].rolling(window=30, min_periods=1).std().fillna(0.0)
                    
                    all_data.append(ticker_df)
                except Exception as e:
                    logger.warning(f"Error processing ticker {ticker}: {e}")
        except Exception as e:
            logger.error(f"Error fetching batch {batch}: {e}")

    if not all_data:
        logger.error("No stock data could be fetched from yfinance.")
        return pd.DataFrame()

    full_df = pd.concat(all_data, ignore_index=True)
    
    # Save local CSV backup
    try:
        full_df.to_csv(backup_file, index=False)
        logger.info(f"Saved local backup dataset with {len(full_df)} records to {backup_file}")
    except Exception as e:
        logger.warning(f"Could not save backup CSV: {e}")

    return full_df

def populate_mongodb(df=None, clear_existing=True):
    """Cleans and bulk inserts stock records into MongoDB collection (ultra-fast vectorized format)."""
    if df is None or df.empty:
        df = fetch_stock_data()
        
    if df.empty:
        logger.error("Dataframe is empty. Aborting database population.")
        return 0

    collection = db_manager.get_collection()
    
    if clear_existing:
        collection.drop()
        logger.info(f"Collection '{db_manager.collection_name}' dropped.")

    logger.info(f"Preparing {len(df)} records for MongoDB insertion using fast vectorization...")
    start_time = time.time()
    
    df_copy = df.copy()
    df_copy['open'] = df_copy['open'].round(4)
    df_copy['high'] = df_copy['high'].round(4)
    df_copy['low'] = df_copy['low'].round(4)
    df_copy['close'] = df_copy['close'].round(4)
    df_copy['volume'] = df_copy['volume'].fillna(0).astype(int)
    df_copy['daily_return'] = df_copy['daily_return'].round(4)
    df_copy['sma_30'] = df_copy['sma_30'].round(4)
    df_copy['volatility_30'] = df_copy['volatility_30'].round(4)
    
    # Convert dates to datetime object
    if not pd.api.types.is_datetime64_any_dtype(df_copy['date']):
        df_copy['date'] = pd.to_datetime(df_copy['date'])
        
    # High-speed conversion to list of dicts
    records = df_copy.to_dict('records')
    
    # Bulk insert in batches of 50,000
    batch_size = 50000
    total_inserted = 0
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        try:
            collection.insert_many(batch, ordered=False)
            total_inserted += len(batch)
            logger.info(f"Inserted {total_inserted}/{len(records)} records into MongoDB...")
        except Exception as e:
            logger.error(f"Error during bulk insert: {e}")

    # Build indexes after bulk insertion for max speed
    db_manager.setup_indexes()

    # Insert sample manual student test ticks
    insert_manual_test_records()

    elapsed = time.time() - start_time
    logger.info(f"MongoDB population complete: {total_inserted} records inserted in {elapsed:.2f} seconds.")
    
    return total_inserted

if __name__ == "__main__":
    df = fetch_stock_data()
    print(f"Total fetched records: {len(df)}")
    count = populate_mongodb(df)
    print(f"Total inserted documents in MongoDB: {count}")
