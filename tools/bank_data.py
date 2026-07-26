import os
from dotenv import load_dotenv
import plaid
from plaid.api import plaid_api
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from datetime import datetime, timedelta
import datetime as dt

load_dotenv()

configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        "clientId": os.getenv("PLAID_CLIENT_ID"),
        "secret": os.getenv("PLAID_SECRET"),
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

def get_sandbox_access_token():
    # Create a fake public token simulating a user connecting their bank
    public_token_request = SandboxPublicTokenCreateRequest(
        institution_id="ins_109508",
        initial_products=[Products("transactions")]
    )
    public_token_response = client.sandbox_public_token_create(public_token_request)
    
    # Exchange it for an access token
    exchange_request = ItemPublicTokenExchangeRequest(
        public_token=public_token_response.public_token
    )
    exchange_response = client.item_public_token_exchange(exchange_request)
    
    return exchange_response.access_token

# function that fetches all account names, types, and balances
def get_balances(access_token):
    request = AccountsBalanceGetRequest(access_token=access_token)
    response = client.accounts_balance_get(request)
    accounts = response.accounts

    return [
        {
            "name": account.name,
            "type": str(account.type),
            "balance": account.balances.current
        }
        for account in accounts
    ]

# function that fetches all transactions from the last 90 days
def get_transactions(access_token: str):
    end_date = dt.date.today()
    start_date = end_date - timedelta(days=90)
    
    request = TransactionsGetRequest(
        access_token=access_token,
        start_date=start_date,
        end_date=end_date
    )
    response = client.transactions_get(request)
    transactions = response.transactions
    
    return [
        {
            "name": t.name,
            "amount": t.amount,
            "date": str(t.date),
            "category": t.category[0] if t.category else "uncategorized"
        }
        for t in transactions
    ]


if __name__ == "__main__":
    access_token = get_sandbox_access_token()
    print(get_balances(access_token))
    print("\n\n")
    print(get_transactions(access_token))