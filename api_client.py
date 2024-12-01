from py_clob_client.client import ClobClient
from dotenv import load_dotenv
import os
import asyncio


class PolymarketAuth:
    def __init__(self, host: str = "https://clob.polymarket.com/"):
        self.host = host
        load_dotenv()
        self.private_key = os.getenv("POLYGON_PRIVATE_KEY")
        if not self.private_key:
            raise ValueError("POLYGON_PRIVATE_KEY not found in .env file")

        self.client = ClobClient(
            host=self.host,
            key=self.private_key,
            chain_id=137,
        )

    async def derive_api_credentials(self):
        try:
            credentials = await self.client.derive_api_key()

            print("\nAdd these to your .env file:")
            print(f"POLYMARKET_API_KEY={credentials.api_key}")
            print(f"POLYMARKET_API_SECRET={credentials.api_secret}")
            print(f"POLYMARKET_API_PASSPHRASE={credentials.api_passphrase}")

            return credentials

        except Exception as e:
            print(f"Error deriving API key: {e}")
            raise


async def main():
    auth = PolymarketAuth()
    await auth.derive_api_credentials()


if __name__ == "__main__":
    asyncio.run(main())
