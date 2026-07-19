from fyers_apiv3 import fyersModel
from src.config import CLIENT_ID, ACCESS_TOKEN

def get_fyers_client():
    if not CLIENT_ID or not ACCESS_TOKEN:
        raise ValueError("API credentials must be set in the .env file")
        
    return fyersModel.FyersModel(
        client_id=CLIENT_ID,
        is_async=False,
        token=ACCESS_TOKEN,
        log_path=""
    )