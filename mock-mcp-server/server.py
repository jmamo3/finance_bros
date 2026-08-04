from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Dummy Financial Server")

@mcp.tool()
def get_stock_price(ticker: str) -> str:
    """Returns the current stock price for a given ticker symbol."""
    # Hardcoded fake data — just like Person 1's dummy tool will return
    return f"The current price of {ticker} is $150.00 (dummy data)"

if __name__ == "__main__":
    mcp.run()