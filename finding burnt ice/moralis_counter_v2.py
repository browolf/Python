import os
import csv
from moralis import evm_api
import sys
import requests
import pandas as pd

#8942 transfers to the first dead address
"""
This version saves the cursor in a text file so you can start from where it left off before. 
But you won't get very far on 40k CUs per day. $70 for 100Mill CU  
the log file of transactions contains the date of the block as well so I can later sum the daily ice burnt
"""

API_KEY = "<your api key>"
CONTRACT_ADDRESS = "0xc335df7c25b72eec661d5aa32a7c2b7b2a1d1874"

"""
Start from scratch, remove and recreate the log files
"""
def reinitalize_files():
    print(f"Re-initalizing files")
    for file in ["burn_data.csv", "cursor.log"]:
        try:
            os.remove(file) if os.path.exists(file) else None
        except PermissionError:
            print("Close the file {file}")    
    with open('burn_data.csv', mode='a', newline='') as file:
        csv.writer(file).writerow(["Block Timestamp","Block","From Address","To Address", "Transaction Hash", "Ice Burnt"])
    open('cursor.log', mode='w').close()          

"""
Get the latest block from the binance chain
"""
def get_latest_block():
    url = 'https://deep-index.moralis.io/api/v2.2/latestBlockNumber/bsc'
    headers = {
    'Accept': 'application/json',
    'X-API-Key': API_KEY
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        sys.exit(f"Could not get latest block")
    

"""
Get 100 transactions from the cursor
"""
def get_transactions(cursor):
  global to_block
  params = {
    "address": "0xc335df7c25b72eec661d5aa32a7c2b7b2a1d1874", 
    "chain": "bsc",
    "from_block": 39750650,
    "limit": 100,
    "order": "ASC",
    "cursor": cursor,
    
  }
  result = evm_api.token.get_token_transfers(
    api_key=API_KEY,
    params=params,
  )
  return result if result else None

"""
Look for transactions send to addresses ending in "dead"
"""
def dead_transaction(tx):
    to_address = tx['to_address'].lower()      
    if to_address.endswith("dead"):
        return True    

"""
Logs the transaction data in a CSV file
"""
def log_transaction(tx):
    value_in_wei = int(tx["value"])
    ice_value = value_in_wei / (10 ** int(tx["token_decimals"]))  
    block_timestamp = tx['block_timestamp']
    #date_part = block_timestamp.split('T')[0]
    date_part = block_timestamp
    with open('burn_data.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([date_part,tx['block_number'],tx['from_address'],tx['to_address'],tx['transaction_hash'], ice_value]) 
    #print(f"{tx['block_number']}")          

"""
Logs the current cursor in a text file
"""
def log_cursor(cursor):
    with open('cursor.log', mode='w') as file:
        file.write(cursor)


current_block = 0
to_block = int(get_latest_block())
print(f"Latest Block: {to_block}")

#Wipes the csv and log file if you want to start from scratch
if input(f"Reinitialize files aka start again? ").lower() == 'y':
    reinitalize_files()

with open('cursor.log', mode='r') as file:
    cursor = file.read().strip()

if not cursor:
    cursor = ""

"""
the first cursor is always blank  but you need to get through the loop to pickup the 2nd cursor. 
On the first run through the page is 0. 

at the end of the run the last cursor is None. 
so you want to be able to save the last not none cursor and exit the loop.
this should mean that you can continue where it left off tomorrow. 
I'm not 100% sure this works. 
"""
page = 0 
while True:
    try:
        if cursor or page==0:
            log_cursor(cursor)
            transactions = get_transactions(cursor)
            for tx in transactions['result']:
                if dead_transaction(tx):
                    log_transaction(tx)
            print(f"Page {page}")
        else:
            sys.exit("No More Transactions")            

        cursor = transactions['cursor']
        page += 1
    except KeyboardInterrupt:
        sys.exit("Manually stopped")




