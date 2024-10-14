import requests
import time

"""
This script falls foul of an undocumented limit on the BSCSCAN.COM api and will only fetch 10k transactions 
on the free account

"""

# BscScan API settings
API_KEY = "<your key>"  # Replace with your BscScan API key
CONTRACT_ADDRESS = "0xc335df7c25b72eec661d5aa32a7c2b7b2a1d1874"
BASE_URL = "https://api.bscscan.com/api"


def get_ice_transactions(contract_address, api_key, page):
    """
    Retrieve transactions for the given token contract from BscScan API.
    """
    params = {
        "module": "account",
        "action": "tokentx",
        "contractaddress": contract_address,
        "startblock": 34934931,
        "endblock": 999999999,
        "page": page,
        "offset": 1000,
        "sort": "asc",
        "apikey": api_key,
    }
    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        return response.json().get("result", [])
    else: 
        print(response.status_code)
        return []

def filter_dead_addresses(transactions):
    total_ice_burned = 0
    dead_pattern = "dead"

    for tx in transactions:
        to_address = tx["to"].lower()
        if to_address.endswith(dead_pattern):
            value_in_wei = int(tx["value"])
            ice_value = value_in_wei / (10 ** int(tx["tokenDecimal"]))
            total_ice_burned += ice_value
    return total_ice_burned        

page = 1
total_ice_burned = 0 
while True:
    #fetch transactions for the current page
    transactions = get_ice_transactions(CONTRACT_ADDRESS, API_KEY, page)
    if not transactions:
        print(f"no transactions in page {page}")
        break # exit if no more transactions found
    #count ice burned in this page
    total_ice_burned += filter_dead_addresses(transactions)
    print(f"Processed page {page} - {total_ice_burned} so far")
    #move to the next page
    page += 1
    time.sleep(5)

print("==============================")
print(f"Total Ice Burned: {total_ice_burned}")

        
