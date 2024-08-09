import os
import requests
from web3 import Web3
import pandas as pd
import re
from datetime import datetime, timedelta, timezone
import sys


#Team Pool 0x02749cD94f45B1ddac521981F5cc50E18CEf3ccC    5.2 bill ice
#Mining Rewards Pool 0xcF03ffFA7D25f803Ff2c4c5CEdCDCb1584C5b32C 2.6 bill ice
#Dao Pool 0x532EFf382Adad223C0a83F3F1f7D8C60d9499a97  3.1 bill ice
#Treasury Pool  0x8c9873C885302Ce2eE1a970498c1665a6DB3D650   2.1 Bill Ice
#Ecosystem Pool 0x8c9873C885302Ce2eE1a970498c1665a6DB3D650  2.1 bill ICe


TEAM_POOL = "0x02749cD94f45B1ddac521981F5cc50E18CEf3ccC"
MINING_POOL = "0xcF03ffFA7D25f803Ff2c4c5CEdCDCb1584C5b32C"
DAO_POOL = "0x532EFf382Adad223C0a83F3F1f7D8C60d9499a97"
TREASURY_POOL = "0x8c9873C885302Ce2eE1a970498c1665a6DB3D650"
ECOSYSTEM_POOL = "0x576fE98558147a2a54fc5f4a374d46d6d9DD0b81"

wallet_lookup = {
    TEAM_POOL: "Team Pool",
    MINING_POOL: "Mining Pool",
    DAO_POOL: "Dao Pool",
    TREASURY_POOL: "Treasury Pool",
    ECOSYSTEM_POOL: "Ecosystem Pool"
}

#the input file is downloaded from
#https://bscscan.com/advanced-filter?fadd=0xeaed594b5926a7d5fbbc61985390baaf936a6b8d&tadd=0xeaed594b5926a7d5fbbc61985390baaf936a6b8d&tkn=0xc335Df7C25b72eEC661d5Aa32a7c2B7b2a1D1874&ps=100&mtd=0x13ef2b1b%7eLock

INPUT_FILE = "lock_transactions.csv"
OUTPUT_FILE = "lock_data.csv"
if os.path.exists(OUTPUT_FILE):
    os.remove(OUTPUT_FILE)
    print(f"Deleted {OUTPUT_FILE}")

#apikey of bscscan
apikey = "<your api key>"
#w3 provider
w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org/'))


#get the input data for a given transaction hash -  contains information inputs to smart contract
def get_transaction_input_data(tx_hash):
    url = f"https://api.bscscan.com/api?module=proxy&action=eth_getTransactionByHash&txhash={tx_hash}&apikey={apikey}"
    response = requests.get(url)
    transaction = response.json().get('result', {})   
    return transaction.get('input', '')      

#convert row['age'], a string containing x days ago to a specific date
def days_ago_to_date(input_string):
    days_ago = int(re.search(r'(\d+) days ago', input_string).group(1))
    today = datetime.today()
    date_ago = today - timedelta(days=days_ago)
    return date_ago.strftime('%Y-%m-%d')


#function to parse the transaction data and return the lock information 
def parse_transaction_data(data):
    
    def unint256_to_token(hex_value):
        integer_value = int(hex_value, 16)
        token_amount = integer_value // (10 ** 18)
        return token_amount    

    def unint256_to_date(hex_value):
        timestamp = int(hex_value, 16)
        date = datetime.fromtimestamp(timestamp, tz=timezone.utc) 
        return date.strftime('%Y-%m-%d')   

    #skip the first 202 characters
    data = data[202:]
    
    #split remaining data into 320 char chunks which represent a lock transaction
    lock_sections = [data[i:i+320] for i in range(0, len(data), 320)]
    
    locks = []
    for lock in lock_sections:
        #split chunk into 64 character sections
        lock_array = [lock[i:i+64] for i in range(0, len(lock), 64)]
        
        # Determine the lock condition
        lock_condition = "none" if lock_array[4] == '0' * 64 else "other"
        
        locks.append({
            #'lock_owner':lock_array[0],
            'lock_amount': unint256_to_token(lock_array[1]),
            #'lock_start': lock_array[2],
            'lock_end': unint256_to_date(lock_array[3]),
            #'lock_condition':lock_condition

        })    
 

    return locks


export_data = []

#read the csv file
df = pd.read_csv(INPUT_FILE)
#print(df)
for _,row in df.iterrows():
    transaction_hash = row['Transaction Hash']
    pool_name = wallet_lookup.get(row['From'], f"{row['From']}")
    lock_amount = row['Amount']
    lock_date = days_ago_to_date(row['Age'])
    
    transaction_data = get_transaction_input_data(transaction_hash)

    print(f"{pool_name}: {lock_amount}, Locked on: {lock_date}, owener address: {row['From']}")
    
    locks = parse_transaction_data(transaction_data)

    print(f"{locks}\n\n")

    for lock in locks:
        export_data.append({
            'Pool_name': pool_name,
            'lock_date' : lock_date,
            'lock_amount': lock['lock_amount'],
            'lock_end': lock['lock_end']
        })

# Create DataFrame from the collected data
df_export = pd.DataFrame(export_data, columns=['Pool_name', 'lock_amount', 'lock_date', 'lock_end'])

# Export DataFrame to CSV
df_export.to_csv(OUTPUT_FILE, index=False)
