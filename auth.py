import os
import webbrowser
from dotenv import load_dotenv
from fyers_apiv3 import fyersModel

# Load the environment variables from your .env file
load_dotenv()

# Fetch the static credentials dynamically
client_id = os.getenv("FYERS_CLIENT_ID")
secret_key = os.getenv("FYERS_SECRET_KEY")
redirect_uri = "https://127.0.0.1"

def generate_daily_token():
    # Failsafe to ensure the .env file is configured correctly
    if not client_id or not secret_key:
        print("Error: FYERS_CLIENT_ID and FYERS_SECRET_KEY must be set in the .env file.")
        return

    session = fyersModel.SessionModel(
        client_id=client_id,
        secret_key=secret_key,
        redirect_uri=redirect_uri,
        response_type="code",
        grant_type="authorization_code"
    )

    # 1. Generate the login link and open it in your default browser
    auth_link = session.generate_authcode()
    print("Opening browser for Fyers Login...")
    webbrowser.open(auth_link)

    # 2. You will log in, and Fyers will redirect you to an empty page.
    # Look at the URL bar. It will look like: 
    # https://127.0.0.1/?s=ok&code=YOUR_AUTH_CODE_HERE&state=None
    
    # 3. Paste just the 'code' portion back into this terminal
    auth_code = input("\nEnter the 'code' parameter from the URL bar: ")

    # 4. Exchange the auth code for your daily access token
    session.set_token(auth_code)
    response = session.generate_token()
    
    if "access_token" in response:
        print("\nSuccess! Copy this into your .env file as FYERS_ACCESS_TOKEN:")
        print("-" * 50)
        print(response["access_token"])
        print("-" * 50)
    else:
        print(f"\nFailed to generate token. Error: {response}")

if __name__ == "__main__":
    generate_daily_token()