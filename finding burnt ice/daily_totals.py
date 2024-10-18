import pandas as pd
import os

output_file = "daily_totals.csv"
os.remove(output_file) if os.path.exists(output_file) else None


# Read the CSV file
df = pd.read_csv('burn_data.csv')

# Convert the 'date' column to datetime format if it's not already
df['Block Timestamp'] = pd.to_datetime(df['Block Timestamp'], format='%Y-%m-%d')

# Group by date and sum the amounts
daily_totals = df.groupby('Block Timestamp')['Ice Burnt'].sum().reset_index()

# Save the result to a new CSV file
daily_totals.to_csv(output_file, index=False)

print("New CSV file with daily totals created.")
