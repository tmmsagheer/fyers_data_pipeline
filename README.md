# Fyers Data Pipeline & Local Data Lake

A robust, incremental data ingestion pipeline for fetching 1-minute OHLCV historical data for Indian Equity stocks (NSE500) via the Fyers API (v3). 

This pipeline is designed as the foundational data layer for a quantitative trading engine. It dynamically handles API constraints, prevents duplicate downloads, stores data in highly compressed formats, and monitors data health.

## Key Upgrades & Features
* **Intelligent Chunking & Resumption:** The Fyers API limits 1-minute data calls to 100 days. This script automatically chunks larger date ranges (e.g., 2017 to present) and tracks the latest downloaded date per ticker to seamlessly resume where it left off.
* **Parquet Storage:** Uses the PyArrow engine to store data in the Parquet format. Parquet provides massive file compression and columnar storage, making read-times for quantitative analysis exponentially faster than traditional CSVs.
* **Rate Limit Throttling:** Built-in safeguards strictly limit API calls to ~170/minute, keeping the account safe from Fyers' 200/minute ban threshold.
* **Data Health Dashboard:** Automatically generates a local `dashboard.html` report after every run, visualizing date ranges, missing data estimates, and overall data integrity across all tickers.

## Prerequisites
* Python 3.8+ (or Anaconda)
* Fyers trading account with API access
* API `client_id` and `access_token`

## Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/tmmsagheer/fyers_data_pipeline.git](https://github.com/tmmsagheer/fyers_data_pipeline.git)
   cd fyers_data_pipeline
2. Install the required dependencies:
   ``` bash
   pip install -r requirements.txt
   ```
    _(Note: This requires `pyarrow` for Parquet compression and `jinja2` for the HTML dashboard)._

3. Create a .env file in the root directory and add your credentials:
   ```
   FYERS_CLIENT_ID="YOUR_CLIENT_ID-100"
   FYERS_ACCESS_TOKEN="YOUR_ACCESS_TOKEN"
   ```
4. Create a `tickers.csv` file in the root directory with the list of symbols you want to download. Ensure the header is named `symbol`.
   ```
   symbol
   NSE:RELIANCE-EQ
   NSE:TCS-EQ
   ```
## Usage
Run the main script to initiate the incremental batch download.
   ```bash
   python main.py
   ```
The script will:

1. Read the target symbols from `tickers.csv`.
2. Check `data/` for existing Parquet files to determine the start dates.
3. Fetch missing data in 99-day chunks, respecting API limits.
4. Merge, deduplicate, and compress the new data into Parquet files.
5. Generate a fresh `dashboard.html` summarizing your data lake.
## Output
**Time-Series Data**: Saved in the `data/` directory as `{SYMBOL}.parquet`.

**Dashboard**: Open `dashboard.html` in any web browser to view the health and completeness of your local data.