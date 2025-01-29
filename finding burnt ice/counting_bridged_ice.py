import os
import csv
import sys
import requests
import pandas as pd
from moralis import evm_api

# Configuration
API_KEY="<YOUR MORALIS API KEY>
ASSET_ADDRESS = "0x1B31606fcb91BaE1DFFD646061f6dD6FB35D0Bb5"
BURN_ADDRESS = "0x0000000000000000000000000000000000000000"
START_BLOCK = 45996462
OUTPUT_FILE = "bridge_data.csv"

# Initialize log file

def initialize_files():
    print("Reinitializing log file...")
    try:
        os.remove(OUTPUT_FILE) if os.path.exists(OUTPUT_FILE) else None
    except PermissionError:
        print(f"Close the file {OUTPUT_FILE} before proceeding.")
    
    with open(OUTPUT_FILE, mode='w', newline='') as file:
        csv.writer(file).writerow(["Block Timestamp", "Block", "From Address", "To Address", "Transaction Hash", "Value"])

# Get latest BSC block

def get_latest_block():
    url = 'https://deep-index.moralis.io/api/v2.2/latestBlockNumber/bsc'
    headers = {'Accept': 'application/json', 'X-API-Key': API_KEY}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
         return response.json()
    else:
        sys.exit("Error fetching latest block.")

# Fetch transactions

def get_transactions(cursor, from_block):
    params = {
        "address": ASSET_ADDRESS,
        "chain": "bsc",
        "from_block": from_block,
        "limit": 100,
        "order": "ASC",
        "cursor": cursor,
    }
    
    result = evm_api.token.get_token_transfers(api_key=API_KEY, params=params)
    return result if result else None

# Check if transaction is a burn transaction

def is_burn_transaction(tx):
    return tx['to_address'].lower() == BURN_ADDRESS.lower()

# Log transaction to CSV

def log_transaction(tx):
    value_in_wei = int(tx["value"])
    asset_value = value_in_wei / (10 ** int(tx["token_decimals"]))  
    block_timestamp = tx['block_timestamp']
    
    with open(OUTPUT_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([block_timestamp, tx['block_number'], tx['from_address'], tx['to_address'], tx['transaction_hash'], asset_value])

# Execution flow

to_block = int(get_latest_block())
print(f"Latest Block: {to_block}")

if input("Reinitialize files (start from scratch)? [y/n]: ").lower() == 'y':
    initialize_files()
    from_block = START_BLOCK
else:
    df = pd.read_csv(OUTPUT_FILE)
    from_block = int(df.iloc[-1]['Block']) + 1 if not df.empty else START_BLOCK
    del df

cursor = ""
page = 0

while True:
    try:
        if cursor or page == 0:
            transactions = get_transactions(cursor, from_block)
            
            if not transactions or 'result' not in transactions:
                print("No more transactions found.")
                break
            
            for tx in transactions['result']:
                if is_burn_transaction(tx):
                    log_transaction(tx)
            
            print(f"Page {page} processed.")
        else:
            sys.exit("No More Transactions")
        
        cursor = transactions.get('cursor', None)
        page += 1
    except KeyboardInterrupt:
        sys.exit("Process manually stopped.")
    except Exception as e:
        print(f"Error: {e}")
        break
