import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("FYERS_CLIENT_ID")
ACCESS_TOKEN = os.getenv("FYERS_ACCESS_TOKEN")

# Rate Limit Configs
# Fyers max is 200/min. We target 170 to maintain a safe buffer.
CALLS_PER_MINUTE = 170
DELAY_BETWEEN_CALLS = 60.0 / CALLS_PER_MINUTE