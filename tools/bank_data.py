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

if __name__ == "__main__":
    access_token = get_sandbox_access_token()
    print(get_balances(access_token))