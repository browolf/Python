import requests
import json
import sys
import os
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError
import asyncio
import _logger
import time

"""
This scripts checks the vested accounts of ICE Network for new transactions because ICE core team are not announcing when tokens get unvested
"""

# Your BscScan API key
API_KEY = '<bsc api key>'

# telegram bot token
BOT_TOKEN = '<bot token>'
CHAT_ID  = '<channel id>'
MAX_MESSAGE_LENGTH = 4096
bot = Bot(BOT_TOKEN)


# Addresses to monitor
ADDRESSES = {
    '0xcF03ffFA7D25f803Ff2c4c5CEdCDCb1584C5b32C': 'rewards',
    '0x02749cD94f45B1ddac521981F5cc50E18CEf3ccC': 'team',
    '0x532EFf382Adad223C0a83F3F1f7D8C60d9499a97': 'dao',
    '0x8c9873C885302Ce2eE1a970498c1665a6DB3D650': 'treasury',
    '0x576fE98558147a2a54fc5f4a374d46d6d9DD0b81': 'ecosystem',
}

# Function to load the last known hashes from file
def load_last_known_hashes(label):
    if os.path.exists(f"{label}.json"):
        with open(f"{label}.json", 'r') as file:
            hashes = json.load(file)
            return set(hashes) if isinstance(hashes, list) else hashes
    return set()

# Function to append new hashes
def append_hashes(label,new_hashes):
    existing_hash_list = load_last_known_hashes(label)
    updated_hash_list = existing_hash_list.union(new_hashes)
    with open(f"{label}.json", 'w') as file:
        json.dump(list(updated_hash_list), file)           

# Function to get token transfers from BscScan API
def get_token_transfers(address):
    url = f'https://api.bscscan.com/api?module=account&action=tokentx&address={address}&startblock=0&endblock=99999999&sort=asc&apikey={API_KEY}'
    response = requests.get(url)
    return response.json()['result']

#split message
def split_message(message):
    """Split a message into parts if it exceeds the maximum length."""
    return [message[i:i + MAX_MESSAGE_LENGTH] for i in range(0, len(message), MAX_MESSAGE_LENGTH)]
    

# Function to send a message via the Telegram bot
async def send_telegram_message(message):
    try:
        parts = split_message(message)
        for part in parts:
            await bot.send_message(chat_id=CHAT_ID, text=part)
    except TelegramError as e:
        print(f"Failed to send message: {e}")

async def main():
    for address,label in ADDRESSES.items():
        #load last known transactions 
        last_hashes = load_last_known_hashes(label)
        #get transactions from bscan
        new_transactions = get_token_transfers(address)
        #extract hashes from transactions
        hashes = set(transaction['hash'] for transaction in new_transactions)
        #figure out if there's new transactions
        new_hashes = hashes - last_hashes
        
        #if new hashes
        if new_hashes:   
            #filter new transactions using new_hashes
            matching_transactions = [
                transaction for transaction in new_transactions
                if transaction['hash'] in new_hashes
            ]

            append_hashes(label, new_hashes)
            _logger.log(f"{label} - {new_hashes}")

            ice_transactions = [
                transaction for transaction in matching_transactions 
                if transaction['tokenSymbol'] == 'ICE'
            ] 
            

            message = f"New Token Transfers Found for {label} ({address}):\n"
            for txn in ice_transactions:
                value = int(txn['value']) / 10**18  # Convert value from Wei
                timestamp = datetime.fromtimestamp(int(txn['timeStamp']), datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                message += (
                    f"\nTxn Hash: {txn['hash']}"
                    f"\nFrom: {txn['from']}"
                    f"\nTo: {txn['to']}"
                    f"\nToken Name: {txn['tokenName']}"
                    f"\nToken Symbol: {txn['tokenSymbol']}"
                    f"\nValue: {value} {txn['tokenSymbol']}"
                    f"\nTimestamp: {timestamp}\n"
                )

            
            #print(message)
            await send_telegram_message(message)
            _logger.log(message)
        else:
            _logger.log(f"no new transactions for {label}")

        time.sleep(60)

        


# Run the main function in the event loop
if __name__ == "__main__":
    asyncio.run(main())
