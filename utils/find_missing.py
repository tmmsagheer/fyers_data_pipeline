import os
import pandas as pd

def find_missing_tickers():
    csv_file = "data/NSE500_Fyers_Format.csv"
    data_dir = "data"
    
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found.")
        return

    # Load the expected 500 symbols
    df = pd.read_csv(csv_file)
    expected_symbols = df['symbol'].dropna().tolist()
    
    missing_symbols = []
    
    for symbol in expected_symbols:
        # Recreate the exact filename string the fetcher uses
        safe_symbol = symbol.replace(":", "_").replace("-", "_")
        filepath = os.path.join(data_dir, f"{safe_symbol}.parquet")
        
        # Check if the file exists on the drive
        if not os.path.exists(filepath):
            missing_symbols.append(symbol)
            
    print(f"Total expected: {len(expected_symbols)}")
    print(f"Total missing: {len(missing_symbols)}\n")
    
    if missing_symbols:
        print("Missing Tickers:")
        for m in missing_symbols:
            print(f" - {m}")

if __name__ == "__main__":
    find_missing_tickers()