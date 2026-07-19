import os
import pandas as pd
from datetime import date
from src.fetcher import DataFetcher
from src.dashboard import generate_dashboard

def main():
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    
    # Read tickers from CSV
    try:
        tickers_df = pd.read_csv("data/NSE500_Fyers_Format.csv")
        symbols = tickers_df['symbol'].dropna().tolist()
    except FileNotFoundError:
        print("Error: tickers.csv not found. Please create it in the root directory.")
        return

    # Set parameters
    start_date = "2017-07-03"
    end_date = date.today().strftime("%Y-%m-%d")
    
    print(f"Initiating pipeline for {len(symbols)} symbols up to {end_date}...")
    
    # 1. Fetch and store data incrementally
    fetcher = DataFetcher()
    fetcher.batch_download(symbols, start_date, end_date, output_dir)
    
    # 2. Generate health dashboard
    generate_dashboard(data_dir=output_dir)

if __name__ == "__main__":
    main()