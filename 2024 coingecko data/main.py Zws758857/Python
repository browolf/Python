import requests
import time
import os
import sys
import sqlite3
from datetime import datetime
import _logger as logger

# Check the operating system
# 'posix' indicates a Unix-like OS, including Linux
if os.name == 'posix':  
    db_path = '/home/root/python/cg2024/data.db'
else:
    db_path = 'data.db'

# Connect to the SQLite database
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Check if the cursor is valid by executing a simple SQL command
    cursor.execute('SELECT 1')
except sqlite3.Error as e:
    print(f"Error connecting to database: {e}")
    sys.exit(1)

# Define the CoinGecko API endpoint for market data
url = "https://api.coingecko.com/api/v3/coins/markets"
params = {
    'vs_currency': 'usd',  # Base currency to get market data in
    'order': 'market_cap_desc',  # Order by market cap descending
    'per_page': 250,  # Number of results per page
    'page': 1  # Page number
}

# Get today's date
today = datetime.now().strftime('%Y-%m-%d')

# Count variables
new_coins = 0
updates = 0

# Function to fetch market data from CoinGecko API
def fetch_market_data(page):
    params['page'] = page
    while True:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429: # too many requests
            print("Rate limit exceeded. waiting 1 min")
            time.sleep(60)    
        else:
            print(f"Failed to fetch data for page {page}. Waiting for 1 minute before retrying...")
            time.sleep(60)

# Function to check if a coin exists in the database
def check_coin_exists(cursor, coin_id):
    cursor.execute("SELECT 1 FROM coins WHERE id = ?", (coin_id,))
    return cursor.fetchone() is not None

# Function to add a coin
def add_coin(cursor, coin_id, coin_name):
    global new_coins
    cursor.execute("INSERT INTO coins (id, name) VALUES (?, ?)", (coin_id, coin_name))
    new_coins += 1

# Function to check if a ranking exists
def check_ranking_exists(cursor, coin_id, date):
    cursor.execute("SELECT 1 FROM ranking WHERE coin_id = ? AND date = ?", (coin_id, date))
    return cursor.fetchone() is not None

# Function to add a ranking entry
def add_ranking(cursor, coin_id, date, market_cap_rank, market_cap, current_price, total_volume):
    global updates
    cursor.execute("INSERT INTO ranking (coin_id, date, mcr, market_cap, current_price, total_volume) VALUES (?, ?, ?, ?, ?, ?)",
                   (coin_id, date, market_cap_rank, market_cap, current_price, total_volume))
    updates += 1

# Function to check if ath/atl data exists
def check_ath_atl_exists(cursor, coin_id):
    cursor.execute("SELECT 1 FROM at WHERE coin_id = ?", (coin_id,))
    return cursor.fetchone() is not None

# Function to add ath/atl data
def add_ath_atl(cursor, coin_id, ath, ath_date, atl, atl_date):
    cursor.execute("INSERT INTO at (coin_id, ath, ath_date, atl, atl_date) VALUES (?, ?, ?, ?, ?)",
                   (coin_id, ath, ath_date, atl, atl_date))

# Function to update ath/atl data
def update_ath_atl(cursor, coin_id, ath, ath_date, atl, atl_date):
    cursor.execute("UPDATE at SET ath = ?, ath_date = ?, atl = ?, atl_date = ? WHERE coin_id = ?",
                   (ath, ath_date, atl, atl_date, coin_id))

# Fetch market data for top 2000 coins
top_coins = []
for page in range(1, 9):  # 2000 coins / 250 coins per page = 8 pages
    data = fetch_market_data(page)
    top_coins.extend(data)
    time.sleep(10)  # Add a delay to respect rate limits

# Extract and display market cap rank and coin name
for coin in top_coins:
    coin_id = coin['id']
    coin_name = coin['name']
    market_cap_rank = coin['market_cap_rank']
    market_cap = coin['market_cap']
    current_price = coin['current_price']
    total_volume = coin['total_volume']
    ath = coin['ath']
    ath_date = coin['ath_date']
    atl = coin['atl']
    atl_date = coin['atl_date']

    if not check_coin_exists(cursor, coin_id):
        add_coin(cursor, coin_id, coin_name)
        print(coin_name)

    if not check_ranking_exists(cursor, coin_id, today):
        add_ranking(cursor, coin_id, today, market_cap_rank, market_cap, current_price, total_volume)
        print(f"{coin_name}, Market Cap Rank: {market_cap_rank}")

    if check_ath_atl_exists(cursor, coin_id):
        update_ath_atl(cursor, coin_id, ath, ath_date, atl, atl_date)
    else:
        add_ath_atl(cursor, coin_id, ath, ath_date, atl, atl_date)

logger.log(f"Coins added: {new_coins}, Coins Updated: {updates}")

conn.commit()
conn.close()
