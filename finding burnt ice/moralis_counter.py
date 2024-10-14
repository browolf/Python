from moralis import evm_api
import sys
import time
import csv
import os

"""
this script using the moralis api managed to count 20mill burnt before running out of daily compute on a free account

"""



if os.path.exists('burn_data.csv'):
    os.remove('burn_data.csv')


API_KEY = "<your api key>"
CONTRACT_ADDRESS = "0xc335df7c25b72eec661d5aa32a7c2b7b2a1d1874"

to_block = 66666666

def get_transactions(cursor):
  params = {
    "address": "0xc335df7c25b72eec661d5aa32a7c2b7b2a1d1874", 
    "chain": "bsc",
    "from_block": 39750680,
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


def filter_dead_address(tx):
  #print(tx)
  #sys.exit()
  ice_value = 0
  to_address = tx['to_address'].lower()
  if to_address.endswith("dead"):
    value_in_wei = int(tx["value"])  
    ice_value = value_in_wei / (10 ** int(tx["token_decimals"]))
    #print(f"{tx['transaction_hash']}  {ice_value} burned")
  return ice_value



cursor = ""
block = 0
ice_burned = 0

with open('burn_data.csv', mode='a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Block", "Burnt"])

    while block < to_block: 
      result = get_transactions(cursor)
      for tx in result['result']:
        ice_burned += filter_dead_address(tx)
      block = int(tx['block_number'])
      cursor = result['cursor']
      print(f"Block {block} Burnt:{ice_burned}")
      writer.writerow([block, ice_burned])
      time.sleep(0.5)  
