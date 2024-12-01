# Import required modules
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
POLYMARKET_API_KEY = os.getenv("POLYMARKET_API_KEY")

# Initialize the backtester with custom parameters
config = TradeConfig(
    min_whale_position=30000,
    market_cap_threshold=0.05,
    follow_percentage=0.05,
    holding_period=20,
)

backtester = WhaleBacktester(config)

# Process historical data and simulate trades
for trade in historical_data:
    if backtester.detect_whale_trade(trade.size, trade.market_cap):
        simulated_trade = backtester.simulate_trade(
            entry_price=trade.price,
            exit_price=trade.price_after_20min,
            position_size=trade.size * config.follow_percentage,
            entry_time=trade.timestamp,
        )
        backtester.trades.append(simulated_trade)

# Analyze results
analytics = StrategyAnalytics(backtester.trades)
metrics = analytics.calculate_metrics()
print(metrics)
