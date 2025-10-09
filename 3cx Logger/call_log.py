"""
Call_Logs.py

This page is part of a **Streamlit multipage server** that displays recent external outgoing calls
from a PostgreSQL database. 

Data is sent to the database using a connector in the 3cx Admin. Unfortunately the schedule is
minimum an hour and then the data is minimum 1 hour old. 

Features included in this page:
- Shows up to 200 of the most recent external outgoing calls.
- Displays call start time, source number, source name, and external number.
- Column names are user-friendly.
- Shows minutes until the next scheduled 3CX export (top-of-hour).

**Important:** Update the DB variables with your PostgreSQL details
before running the app.

"""

import streamlit as st
import pandas as pd
import psycopg2
import datetime

st.set_page_config(page_title="External Calls", layout="wide")
st.title("External Outgoing Calls")

DB_HOST = "127.0.0.1"
DB_NAME = "<db name>"
DB_USER = "<db user>"
DB_PASSWORD = "<db password>"
DB_PORT = 5432
EXPORT_INTERVAL_HOURS = 1  # 3CX scheduled export interval

@st.cache_data(ttl=300)
def load_data():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )

    query = """
        SELECT 
            to_char(cdr_started_at, 'YYYY-MM-DD HH24:MI') AS call_start,
            source_dn_number,
            source_dn_name,
            COALESCE(destination_participant_phone_number, destination_dn_number) AS external_number
        FROM cdroutput
        WHERE destination_dn_name = 'Outgoing Call - General'
        ORDER BY cdr_started_at DESC
        LIMIT 200;
    """

    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Load data
data = load_data()

# Calculate time until next scheduled export
now = datetime.datetime.now()
minutes_remaining = 59 - now.minute  # minutes until the next full hour
st.info(f"Next scheduled export in: {minutes_remaining} minutes")


# Display the table
st.write(f"Showing {len(data)} recent external outgoing calls")
#table_data = data.reset_index(drop=True)

# Rename columns
table_data = data.rename(columns={
    "call_start": "Call Time",
    "source_dn_number": "Source Number",
    "source_dn_name": "Source Name",
    "external_number": "External Number"
})

st.table(table_data)
