import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mcp.server.fastmcp import FastMCP
from tools.market_data import get_stock_price, get_stock_overview
from tools.bank_data import get_balances, get_transactions
from tools.reddit_data import get_reddit_sentiment

mcp = FastMCP("Financial Advisor Server")

@mcp.tool()
def stock_price(ticker: str) -> str:
    """Returns the current stock price for a given ticker symbol."""
    return str(get_stock_price(ticker))

@mcp.tool()
def stock_overview(ticker: str) -> str:
    """Returns fundamental data for a company including PE ratio, market cap, and analyst targets."""
    return str(get_stock_overview(ticker))

@mcp.tool()
def reddit_sentiment(ticker: str) -> str:
    """Returns recent Reddit posts about a ticker for sentiment analysis."""
    return str(get_reddit_sentiment(ticker))

@mcp.tool()
def balances(access_token: str) -> str:
    """Returns current balances for all bank accounts."""
    return str(get_balances(access_token))

@mcp.tool()
def transactions(access_token: str) -> str:
    """Returns transactions from the last 90 days."""
    return str(get_transactions(access_token))

if __name__ == "__main__":
    mcp.run()