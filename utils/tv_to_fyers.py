import os
import pandas as pd

def format_tradingview_tickers():
    files_to_process = [
        {"input": "data/NSE500_All.csv", "output": "data/NSE500_Fyers_Format.csv"},
        {"input": "data/NSE500Momentum50_All.csv", "output": "data/NSE500Momentum50_Fyers_Format.csv"}
    ]

    # Map TradingView anomalies back to official NSE formats
    ticker_map = {
        "BAJAJ_AUTO": "BAJAJ-AUTO",
        "NAM_INDIA": "NAM-INDIA",
        "M_M": "M&M",         # Added proactively as TradingView also alters Mahindra & Mahindra
        "M_MFIN": "M&MFIN", 
        "L_TFH": "L&TFH"
    }

    for file_map in files_to_process:
        input_file = file_map["input"]
        output_file = file_map["output"]

        if not os.path.exists(input_file):
            continue
            
        try:
            df = pd.read_csv(input_file)
            
            # 1. Clean the string 
            clean_symbols = df['Symbol'].astype(str).str.strip()
            
            # 2. Apply the dictionary map to fix the underscores
            clean_symbols = clean_symbols.replace(ticker_map)
            
            # 3. Format for Fyers
            output_df = pd.DataFrame()
            output_df['symbol'] = 'NSE:' + clean_symbols + '-EQ'
            
            output_df.to_csv(output_file, index=False)
            print(f"Success: Converted {len(output_df)} tickers from {input_file}")
            
        except Exception as e:
            print(f"Failed to process {input_file}. Error: {str(e)}")

if __name__ == "__main__":
    format_tradingview_tickers()