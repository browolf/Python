import requests
import pandas as pd
import datetime as dt

# Function to get historical data from Binance
def get_binance_historical_data(symbol, interval, start_date, end_date):
    base_url = "https://api.binance.com/api/v3/klines"
    url = f"{base_url}?symbol={symbol}&interval={interval}&startTime={int(start_date.timestamp() * 1000)}&endTime={int(end_date.timestamp() * 1000)}"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
    df['Close'] = df['Close'].astype(float)
    df['Date'] = pd.to_datetime(df['Close time'], unit='ms')
    return df[['Date', 'Close']]

# Prompt the user for the start date
start_date_str = input("Enter the start date (YYYY-MM-DD): ")
start_date = dt.datetime.strptime(start_date_str, '%Y-%m-%d')

# Define the end date as today
end_date = dt.datetime.now()

# Get the historical data
btc_data = get_binance_historical_data("BTCUSDT", "1w", start_date, end_date)

# Add a column for the investment amount ($10 every week)
btc_data['Investment'] = 10

# Add a column for cumulative investment
btc_data['Cumulative_Investment'] = btc_data['Investment'].cumsum()

# Add a column for the amount of BTC bought each week
btc_data['BTC_Bought'] = btc_data['Investment'] / btc_data['Close']

# Add a column for cumulative BTC bought
btc_data['Cumulative_BTC'] = btc_data['BTC_Bought'].cumsum()

# Calculate the current value of the cumulative BTC
current_btc_value = btc_data['Cumulative_BTC'].iloc[-1] * btc_data['Close'].iloc[-1]

# Calculate the total amount invested
total_invested = btc_data['Cumulative_Investment'].iloc[-1]

# Calculate profit/loss
profit_loss = current_btc_value - total_invested

# Display the results
print(f"Total Amount Invested: ${total_invested:.2f}")
print(f"Current Value of Bitcoin Holdings: ${current_btc_value:.2f}")
print(f"Profit/Loss: ${profit_loss:.2f}")
