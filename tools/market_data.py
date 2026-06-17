import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ALPHA_VANTAGE_KEY")

def get_stock_price(ticker: str) :
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": ticker,
        "apikey": API_KEY
    }

    response = requests.get(url, params = params)
    data = response.json()
    quote = data.get("Global Quote", {})

    if not quote:
        return {"error": f"No information found for ticker {ticker}"}

    return {
        "ticker": ticker,
        "price": quote.get("05. price"),
        "change": quote.get("09. change"),
        "change percent": quote.get("10. change percent"),
        "volume": quote.get("06. volume")
    }


if __name__ == "__main__" :
    ticker = input("Enter ticker symbol: ").upper()
    print(get_stock_price(ticker))