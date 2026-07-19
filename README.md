# Fyers Data Pipeline & Local Data Lake

A robust, incremental data ingestion pipeline for fetching 1-minute OHLCV historical data for Indian Equity stocks (NSE500) via the Fyers API (v3). 

This pipeline is designed as the foundational data layer for a quantitative trading engine. It dynamically handles API constraints, prevents duplicate downloads, stores data in highly compressed formats, and monitors data health via a local dashboard.

## Architecture & Project Structure
* `src/config.py`: Configuration parameters and API rate limit buffers.
* `src/client.py`: API initialization script utilizing environment variables.
* `src/fetcher.py`: The core ingestion loop managing 100-day chunking, deduplication, and Parquet writing.
* `src/dashboard.py`: Scans data layers to generate a local data integrity health report.
* `auth.py`: Interactive script for generating the daily regulatory-mandated access token.
* `main.py`: Main orchestration entry point.

## Key Features
* **Secure Token Separation:** `auth.py` reads your static App ID and Secret Key securely from `.env` to execute the OAuth flow, ensuring no keys are hardcoded.
* **Intelligent Chunking & Resumption:** Automatically splits large date ranges into 99-day windows to satisfy Fyers API limitations. It auto-detects existing local checkpoints to fetch only new candles.
* **High-Performance Storage:** Data is stored using the PyArrow engine in Parquet format, offering massive disk space compression and accelerated read speeds for time-series analysis.
* **Terminal UI Progress Tracker:** Uses `tqdm` to provide visual telemetry inside the terminal while piping granular troubleshooting statements out of view to a freshly overwritten `pipeline.log` file.

## Prerequisites
* Python 3.8+ (or Anaconda environment)
* An active Fyers trading account with API access enabled
* A registered Fyers App pointing to `https://127.0.0.1` as the Redirect URI

## Installation & First-Time Setup

1. Clone the repository:
   ```bash
   git clone [https://github.com/yourusername/fyers_data_pipeline.git](https://github.com/yourusername/fyers_data_pipeline.git)
   cd fyers_data_pipeline
   ```
2. Create a virtual environment and install dependencies:
   ``` bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
    _(Note: This requires `pyarrow` for Parquet compression and `jinja2` for the HTML dashboard)._

3. Create a .env file in the root directory and add your credentials:
   ```
   FYERS_CLIENT_ID="YOUR_CLIENT_ID-100"
   FYERS_SECRET_KEY="YOUR_SECRET_KEY"
   FYERS_ACCESS_TOKEN="YOUR_ACCESS_TOKEN"
   ```
4. Create a `tickers.csv` file in the root directory with the list of symbols you want to download. Ensure the header is named `symbol`.
   ```
   symbol
   NSE:RELIANCE-EQ
   NSE:TCS-EQ
   ```
## Usage
Because Indian regulations dictate that Fyers access tokens expire daily, run through these two steps every day you ingest data:

### Step 1: Refresh Your Token
Run the authentication script to generate a valid session string:
```bash
python auth.py
```
- The script automatically opens your default web browser to log into Fyers.
- Upon successful authentication, the browser redirects to a broken page (`127.0.0.1`).
- Copy the `code` value from the URL parameter in your browser's address bar.
- Paste the string back into your terminal prompt and press **Enter**.
- Copy the generated token string outputted by the script and assign it to `FYERS_ACCESS_TOKEN` in your `.env` file.
### Step 2: Ingest the Data
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
- **Time-Series Data**: Saved in the `data/` directory as `{SYMBOL}.parquet`.
- **Health Metrics**: Open `dashboard.html` in any web browser to view active structural coverage dates, total captured rows, and calculated telemetry gaps.
- **Logs**: Diagnostic step reports are sent directly to `pipeline.log`, which auto-overwrites with every new pipeline pass.