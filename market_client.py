from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL
from config import PolymarketConfig  # Add this import
import os


class PolymarketClient:
    def __init__(self, config: PolymarketConfig):
        self.config = config

        # Use private key from environment variable
        private_key = os.getenv("POLYGON_PRIVATE_KEY")
        if not private_key:
            raise ValueError("POLYGON_PRIVATE_KEY environment variable is required")

        # Remove 0x prefix if present
        if private_key.startswith("0x"):
            private_key = private_key[2:]

        self.clob_client = ClobClient(
            host=config.REST_ENDPOINT,
            key=private_key,  # Pass private key instead of API key
            chain_id=137,  # Polygon mainnet
        )

    async def get_market_data(self, condition_id: str):
        """Get market data including book depth and midpoint"""
        market = await self.clob_client.get_market(condition_id)
        book = await self.clob_client.get_book(condition_id)
        midpoint = await self.clob_client.get_midpoint(condition_id)
        return market, book, midpoint

    async def place_order(self, market_id: str, side: str, size: float, price: float):
        """Place a limit order"""
        order_args = OrderArgs(
            token_id=market_id,
            price=price,
            size=size,
            side=BUY if side == "buy" else SELL,
            fee_rate_bps=0,  # Fee rate from documentation
        )

        try:
            response = await self.clob_client.post_order(
                order=order_args,
                order_type=OrderType.GTC,  # Good-til-cancelled
            )
            return response
        except Exception as e:
            print(f"Error placing order: {e}")
            return None
