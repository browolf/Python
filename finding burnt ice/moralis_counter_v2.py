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
output_burnt = "burn_data.csv"
cursor_log = "cursor.log"

"""
Start from scratch, remove and recreate the log files
"""
def reinitalize_files():
    print(f"Re-initalizing files")
    for file in [output_burnt, cursor_log]:
        try:
            os.remove(file) if os.path.exists(file) else None
        except PermissionError:
            print("Close the file {file}")    
    with open(output_burnt, mode='a', newline='') as file:
        csv.writer(file).writerow(["Block Timestamp","Block","From Address","To Address", "Transaction Hash", "Ice Burnt"])
    open(cursor_log, mode='w').close()          

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
def get_transactions(cursor, from_block):
  global to_block
  params = {
    "address": "0xc335df7c25b72eec661d5aa32a7c2b7b2a1d1874", 
    "chain": "bsc",
    "from_block": from_block,
    "limit": 100,
    "order": "ASC",
    "cursor": cursor,
    
  }
  result = evm_api.token.get_token_transfers(
    api_key=API_KEY,
    params=params,
  )
  return result if result else None


def dead_transaction(tx):
    to_address = tx['to_address'].lower()      
    if to_address.endswith("dead"):
        return True    

def log_transaction(tx):
    value_in_wei = int(tx["value"])
    ice_value = value_in_wei / (10 ** int(tx["token_decimals"]))  
    block_timestamp = tx['block_timestamp']
    #date_part = block_timestamp.split('T')[0]
    date_part = block_timestamp
    with open(output_burnt, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([date_part,tx['block_number'],tx['from_address'],tx['to_address'],tx['transaction_hash'], ice_value]) 
    #print(f"{tx['block_number']}")          


def log_cursor(cursor):
    with open(cursor_log, mode='w') as file:
        file.write(cursor)


current_block = 0
to_block = int(get_latest_block())
print(f"Latest Block: {to_block}")

if input(f"Reinitialize files aka start again? ").lower() == 'y':
    reinitalize_files()
    from_block = 39752100
else:
    #get last block from csv file
    df = pd.read_csv(output_burnt)
    last_row = df.iloc[-1]
    from_block = int(last_row['Block'])+1
    del df

        

#with open(cursor_log, mode='r') as file:
#    cursor = file.read().strip()

cursor = ""
page = 0 
while True:
    try:
        if cursor or page == 0:
            #log_cursor(cursor)
            transactions = get_transactions(cursor, from_block)
            for tx in transactions['result']:
                if dead_transaction(tx):
                    log_transaction(tx)
            print(f"Page {page}")
        else:
            #log_cursor("")
            sys.exit("No More Transactions")            

        cursor = transactions['cursor']
        page += 1
    except KeyboardInterrupt:
        sys.exit("Manually stopped")
    




