import pandas as pd
import os

output_file = "daily_bridged_totals.csv"
os.remove(output_file) if os.path.exists(output_file) else None


# Read the CSV file
df = pd.read_csv('bridge_data.csv')

# Convert the 'date' column to datetime format if it's not already
df['Date Part'] = df['Block Timestamp'].str.split('T').str[0]
df['Date Part'] = pd.to_datetime(df['Date Part'], format='%Y-%m-%d')

print(df)

# Group by date and sum the amounts
#daily_totals = df.groupby(df['Date Part'].dt.date)['Ice Burnt'].sum().reset_index()

# Group by date and sum the amounts, and count the number of items
daily_totals = df.groupby(df['Date Part'].dt.date).agg(
    total_ice_burnt=('Value', 'sum'),
    item_count=('Value', 'size')  # Count the number of items per date
).reset_index()


# Save the result to a new CSV file
daily_totals.to_csv(output_file, index=False)

print("New CSV file with daily totals created.")
print(f"burnt total: {df['Value'].sum()}")
