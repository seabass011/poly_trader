from dataclasses import dataclass
from typing import List, Dict
import time
from market_client import PolymarketClient
from config import TradeConfig, PolymarketConfig


@dataclass
class PolymarketConfig:
    API_KEY: str
    API_SECRET: str
    API_PASSPHRASE: str


@dataclass
class TradeConfig:
    min_whale_position: float
    market_cap_threshold: float
    follow_percentage: float
    holding_period: int


@dataclass
class Trade:
    market_id: str
    side: str
    size: float
    price: float
    timestamp: int
    trade_id: str
    maker_orders: List[Dict]
    status: str


class WhaleBacktester:
    def __init__(self, trade_config: TradeConfig, poly_config: PolymarketConfig):
        self.config = trade_config
        self.client = PolymarketClient(poly_config)
        self.trades: List[Trade] = []
        self.positions: Dict[str, float] = {}
        self.last_processed_time = int(time.time()) - (24 * 60 * 60)  # Start 24h ago

    async def get_historical_trades(self, market_id: str) -> List[Trade]:
        """Fetch historical trades for a market"""
        try:
            trades = await self.client.get_trades(
                {"market": market_id, "after": str(self.last_processed_time)}
            )

            return [
                Trade(
                    market_id=trade["market"],
                    side=trade["side"],
                    size=float(trade["size"]),
                    price=float(trade["price"]),
                    timestamp=int(trade["matchtime"]),
                    trade_id=trade["id"],
                    maker_orders=trade["maker_orders"],
                    status=trade["status"],
                )
                for trade in trades
                if trade["status"] == "CONFIRMED"
            ]
        except Exception as e:
            print(f"Error fetching historical trades: {e}")
            return []

    async def detect_whale_trade(self, trade: Trade) -> bool:
        """Enhanced whale trade detection using trade data and market context"""
        try:
            book = await self.client.get_orderbook(trade.market_id)

            # Calculate market impact
            trade_value = trade.size * trade.price
            market_depth = sum(
                float(level["size"]) * float(level["price"])
                for level in book["buys"] + book["sells"]
            )

            # Consider a trade "whale" if:
            # 1. Size exceeds minimum threshold
            # 2. Trade value is significant vs market depth
            # 3. Trade moves price significantly
            is_whale = (
                trade.size >= self.config.min_whale_position
                and trade_value >= market_depth * self.config.market_cap_threshold
            )

            if is_whale:
                print(f"Whale trade detected: {trade.trade_id}")
                print(f"Size: {trade.size}, Price: {trade.price}")
                print(f"Market Impact: {(trade_value/market_depth)*100:.2f}%")

            return is_whale

        except Exception as e:
            print(f"Error in whale detection: {e}")
            return False

    async def process_market(self, market_id: str):
        """Process all trades for a market"""
        trades = await self.get_historical_trades(market_id)

        for trade in trades:
            if await self.detect_whale_trade(trade):
                # Execute follow trade
                follow_trade = await self.execute_trade(
                    market_id=trade.market_id,
                    side=trade.side,
                    size=trade.size,
                    price=trade.price,
                )

                if follow_trade:
                    self.trades.append(trade)
                    # Update position tracking
                    self.positions[market_id] = self.positions.get(market_id, 0) + (
                        trade.size if trade.side == "BUY" else -trade.size
                    )

        self.last_processed_time = int(time.time())

    async def execute_trade(self, market_id: str, side: str, size: float, price: float):
        """Execute trade through Polymarket CLOB with position sizing"""
        return await self.client.place_order(
            market_id=market_id,
            side=side,
            size=size * self.config.follow_percentage,
            price=price,
        )


async def run_whale_tracker(
    market_ids: List[str], trade_config: TradeConfig, poly_config: PolymarketConfig
):
    """Run whale tracker on specified markets"""
    tracker = WhaleBacktester(trade_config, poly_config)

    print(f"Starting whale tracking for {len(market_ids)} markets...")
    for market_id in market_ids:
        print(f"\nProcessing market: {market_id}")
        try:
            await tracker.process_market(market_id)

            # Print market summary
            market_trades = [t for t in tracker.trades if t.market_id == market_id]
            market_position = tracker.positions.get(market_id, 0)

            print("\nMarket Summary:")
            print(f"Total Whale Trades: {len(market_trades)}")
            print(f"Current Position: {market_position}")

            # Print individual trades
            if market_trades:
                print("\nDetailed Trades:")
                for trade in market_trades:
                    print(f"Trade ID: {trade.trade_id}")
                    print(f"Side: {trade.side}")
                    print(f"Size: {trade.size:,.2f}")
                    print(f"Price: ${trade.price:.4f}")
                    print("---")

        except Exception as e:
            print(f"Error processing market {market_id}: {e}")

    return tracker


if __name__ == "__main__":
    from config import TradeConfig, PolymarketConfig
    import asyncio

    # Example market IDs - replace with actual market IDs you want to track
    MARKET_IDS = [
        "71321045679252212594626385532706912750332728571942532289631379312455583992563",  # Example market ID
    ]

    # Load configs
    trade_config = TradeConfig()
    poly_config = PolymarketConfig()

    # Run tracker
    print("Starting Polymarket Whale Tracker...")
    print(f"Min Whale Position: {trade_config.min_whale_position:,.0f}")
    print(f"Market Cap Threshold: {trade_config.market_cap_threshold:.1%}")
    print(f"Follow Percentage: {trade_config.follow_percentage:.1%}")

    tracker = asyncio.run(run_whale_tracker(MARKET_IDS, trade_config, poly_config))

    # Print final summary
    print("\nFinal Summary:")
    print(f"Total Markets Tracked: {len(MARKET_IDS)}")
    print(f"Total Whale Trades: {len(tracker.trades)}")
    print("\nCurrent Positions:")
    for market_id, position in tracker.positions.items():
        print(f"Market {market_id}: {position:,.2f}")
