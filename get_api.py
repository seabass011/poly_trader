from py_clob_client.client import ClobClient
import os
import secrets


def generate_private_key():
    """Generate a new private key in correct hex format"""
    # Generate random private key
    priv = secrets.token_hex(32)
    return priv


# Either generate new or use existing private key
private_key = os.getenv("POLYGON_PRIVATE_KEY") or generate_private_key()

# Initialize client
client = ClobClient(
    host="https://clob.polymarket.com/",
    key=private_key,  # Must be hex string without 0x prefix
    chain_id=137,  # Polygon mainnet
)

try:
    # Create API credentials
    credentials = client.create_api_key()

    print("Successfully created API credentials:")
    print(f"API Key: {credentials['apiKey']}")
    print(f"Secret: {credentials['secret']}")
    print(f"Passphrase: {credentials['passphrase']}")

    print("\nAdd these to your .env file:")
    print(f"POLYMARKET_API_KEY={credentials['apiKey']}")
    print(f"POLYMARKET_SECRET={credentials['secret']}")
    print(f"POLYMARKET_PASSPHRASE={credentials['passphrase']}")

except Exception as e:
    print(f"Error creating API key: {e}")
