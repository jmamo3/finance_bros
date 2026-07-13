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

def get_stock_overview(ticker: str) :
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "OVERVIEW",
        "symbol": ticker,
        "apikey": API_KEY
    }

    response = requests.get(url, params = params)
    data = response.json()
   
    if not data or "Symbol" not in data:
        return {"error": f"No overview found for ticker {ticker}"}

    return {
        "ticker": ticker,
        "sector": data.get("Sector"),
        "market_cap": data.get("MarketCapitalization"),
        "pe_ratio": data.get("PERatio"),
        "eps": data.get("EPS"),
        "analyst_target_price": data.get("AnalystTargetPrice"),
        "52_week_high": data.get("52WeekHigh"),
        "52_week_low": data.get("52WeekLow"),
    }

if __name__ == "__main__" :
    ticker = input("Enter ticker symbol: ").upper()
    choice = 0
    while choice != 3 :
        choice = int(input("To fetch current stock price, enter 1.\nTo fetch current stock overview, enter 2.\nTo exit, enter 3.\nYour choice: "))
        if not (choice >= 1 and choice <= 3):
            print("Choice is invalid. Try again!\n")
            continue
        if choice == 1:
            print(get_stock_price(ticker))
        elif choice == 2:
            print(get_stock_overview(ticker))
    print("You have successfully exited.")