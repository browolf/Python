import os
import csv
from moralis import evm_api
import sys
import requests

"""
This version saves the cursor in a text file so you can start from where it left off before. 
But you don't get very far on 40k CUs per day. Might have to pay for a month. 
the log file of transactions contains the date of the block as well so I can later sum the daily ice burnt
the script gets 50 cursors at a time, you can track the CU usage on the moralis portal in nearly real time. 
"""

API_KEY = "<your api_key>"
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
        csv.writer(file).writerow(["Block Timestamp","Transaction Hash", "Ice Burnt"])
    open('cursor.log', mode='w').close()          

"""
Get the latest block number
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
    "from_block": 39750680 ,
    "to_block": to_block,
    "limit": 100,
    "order": "ASC",
    "cursor": cursor,
    
  }
  result = evm_api.token.get_token_transfers(
    api_key=API_KEY,
    params=params,
  )
  return result


def dead_transaction(tx):
    to_address = tx['to_address'].lower()   
    if to_address.endswith("dead"):
        return True    

def log_transaction(tx):
    value_in_wei = int(tx["value"])
    ice_value = value_in_wei / (10 ** int(tx["token_decimals"]))  
    block_timestamp = tx['block_timestamp']
    date_part = block_timestamp.split('T')[0]
    with open('burn_data.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([date_part,tx['transaction_hash'], ice_value])       


current_block = 0
to_block = int(get_latest_block())
print(f"Latest Block: {to_block}")

#if input(f"Reinitialize files aka start again? ").lower() == 'y':
    #reinitalize_files()

with open('cursor.log', mode='r') as file:
    cursor = file.read().strip()


i = 0
while current_block < to_block and i < 50:
    transactions = get_transactions(cursor)
    for tx in transactions['result']:
        if dead_transaction(tx):
            log_transaction(tx)
        

    current_block = int(tx['block_number'])        
    with open('cursor.log', mode='w') as file:
        file.write(transactions['cursor'])
    
    
    #print(f"Length of this selection: {len(tx)}")
    print(f"Current_block: {current_block}")
    cursor = transactions['cursor']
    i +=1
    




