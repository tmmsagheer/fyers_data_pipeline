import os
import time
import logging
from datetime import datetime, timedelta
import pandas as pd
from tqdm import tqdm
from src.client import get_fyers_client
from src.config import DELAY_BETWEEN_CALLS

# Configure logging to write to a file and overwrite it each run ('w')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log", mode='w', encoding='utf-8')
    ]
)

class DataFetcher:
    def __init__(self):
        logging.info("Initializing Fyers API Client...")
        self.fyers = get_fyers_client()
        logging.info("Fyers API Client initialized successfully.")
        
    def fetch_symbol_chunk(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        data = {
            "symbol": symbol,
            "resolution": "1",
            "date_format": "1",
            "range_from": start_date,
            "range_to": end_date,
            "cont_flag": "1"
        }
        
        try:
            response = self.fyers.history(data=data)
            if response.get("s") == "ok":
                columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
                df = pd.DataFrame(response['candles'], columns=columns)
                if not df.empty:
                    df['datetime'] = pd.to_datetime(df['datetime'], unit='s')
                    df['datetime'] = df['datetime'].dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
                return df
            else:
                logging.error(f"API Error for {symbol} ({start_date} to {end_date}): {response.get('message', response)}")
                return pd.DataFrame()
        except Exception as e:
            logging.error(f"Exception occurred while fetching {symbol}: {str(e)}", exc_info=True)
            return pd.DataFrame()

    def batch_download(self, symbols: list, start_date_str: str, end_date_str: str, output_dir: str):
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        logging.info(f"Starting batch download pipeline for {len(symbols)} symbols. Target Range: {start_date_str} to {end_date_str}")
        
        # Initialize terminal progress bar
        progress_bar = tqdm(symbols, desc="Downloading NSE500 1-Min Data", unit="ticker")
        
        for symbol in progress_bar:
            # Update the progress bar side-text with the active asset
            progress_bar.set_postfix_str(f"Active: {symbol.split(':')[-1]}")
            
            safe_symbol = symbol.replace(":", "_").replace("-", "_")
            filepath = os.path.join(output_dir, f"{safe_symbol}.parquet")
            
            current_start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            existing_df = pd.DataFrame()
            
            # Check for existing data to resume incrementally
            if os.path.exists(filepath):
                logging.info(f"Found existing data storage for {symbol} at {filepath}. Checking checkpoints...")
                try:
                    existing_df = pd.read_parquet(filepath)
                    if not existing_df.empty:
                        max_date = existing_df['datetime'].max().date()
                        if max_date >= end_date:
                            logging.info(f"Checkpoint verified: {symbol} is completely up to date (Max date: {max_date}). Skipping execution.")
                            continue
                        
                        current_start_date = max_date + timedelta(days=1)
                        logging.info(f"Checkpoint verified: Resuming {symbol} incrementally from next missing date: {current_start_date}")
                except Exception as e:
                    logging.error(f"Failed to read existing Parquet file for {symbol}. Re-fetching full history. Error: {str(e)}")
            
            new_data_frames = []
            chunk_start = current_start_date
            
            # Chunking logic for historical data limits
            while chunk_start <= end_date:
                chunk_end = min(chunk_start + timedelta(days=99), end_date)
                
                logging.info(f"Dispatching API call for {symbol} | Range: {chunk_start} to {chunk_end}")
                df = self.fetch_symbol_chunk(symbol, chunk_start.strftime("%Y-%m-%d"), chunk_end.strftime("%Y-%m-%d"))
                
                if not df.empty:
                    new_data_frames.append(df)
                    logging.info(f"Successfully retrieved {len(df)} candles for {symbol} in chunk {chunk_start} to {chunk_end}")
                else:
                    logging.warning(f"No records returned or API failed for {symbol} in chunk {chunk_start} to {chunk_end}")
                    
                time.sleep(DELAY_BETWEEN_CALLS)  # Protect rate limits
                chunk_start = chunk_end + timedelta(days=1)
                
            # Merge, deduplicate, and compress data lake layer
            if new_data_frames:
                combined_new_df = pd.concat(new_data_frames, ignore_index=True)
                final_df = pd.concat([existing_df, combined_new_df], ignore_index=True) if not existing_df.empty else combined_new_df
                
                initial_count = len(final_df)
                final_df = final_df.drop_duplicates(subset=['datetime']).sort_values('datetime')
                dropped_count = initial_count - len(final_df)
                
                if dropped_count > 0:
                    logging.info(f"Deduplication pass: Dropped {dropped_count} overlapping duplicate rows for {symbol}.")
                
                final_df.to_parquet(filepath, engine='pyarrow', compression='snappy')
                logging.info(f"Data Lake Sync Complete: Written {symbol} to storage. Complete structural row count: {len(final_df)}")
            else:
                logging.info(f"No new historical windows required update for {symbol} during this execution execution pass.")

        progress_bar.close()
        logging.info("Batch download routine completed execution across all targets.")