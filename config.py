from dotenv import load_dotenv
import os
from dataclasses import dataclass

load_dotenv()


@dataclass
class PolymarketConfig:
    # API Configuration
    API_KEY: str = os.getenv("POLYMARKET_API_KEY")
    API_SECRET: str = os.getenv("POLYMARKET_SECRET")
    API_PASSPHRASE: str = os.getenv("POLYMARKET_PASSPHRASE")

    # Network Configuration
    NETWORK: str = os.getenv("NETWORK", "polygon")  # or 'mumbai' for testnet
    WSS_ENDPOINT: str = "wss://ws-subscriptions-clob.polymarket.com/ws/"
    REST_ENDPOINT: str = "https://clob.polymarket.com/"


@dataclass
class TradeConfig:
    min_whale_position: float = float(os.getenv("MIN_WHALE_POSITION", 30000))
    market_cap_threshold: float = float(os.getenv("MARKET_CAP_THRESHOLD", 0.05))
    follow_percentage: float = float(os.getenv("FOLLOW_PERCENTAGE", 0.05))
    holding_period: int = int(os.getenv("HOLDING_PERIOD", 20))
    slippage: float = float(os.getenv("SLIPPAGE", 0.001))
    trading_fee: float = float(os.getenv("TRADING_FEE", 0.002))
