import streamlit as st
import sqlite3
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
import platform

#for testing 
if platform.system() == "Windows":
    conn = sqlite3.connect('D:\python\streamlit\data.db')
else:    
    conn = sqlite3.connect('/home/root/python/cg2024/data.db')

#function to fetch the list of names and coin_ids
def get_coin_names() -> DataFrame:
    query = 'SELECT * FROM coins'
    df = pd.read_sql_query(query,conn)
    return df

#function to fetch mcr and date for a given coin_id
def get_ranking_data(coin_id:str) -> DataFrame:
    query = 'SELECT date, mcr FROM ranking WHERE coin_id = ?'
    df = pd.read_sql_query(query, conn, params=(coin_id,))
    return df

#streamlit page
st.title('MCR Graph for Selected Coin')

#get list of names
df_coins = get_coin_names()
names = df_coins['name'].tolist()
coin_ids = df_coins.set_index('name')['id'].to_dict()

#text input for filtering
search_term = st.text_input('Search for a coin', '')

#filter names based on search
filtered_names = [name for name in names if search_term.lower() in name.lower()]

#dropdown for selecting a coin name
#selected_name = st.selectbox('Select a coin', names)
selected_name = st.selectbox('Select a coin', filtered_names)

#get the corresponding coin_id
selected_coin_id = coin_ids[selected_name]

#fetch ranking data
df_ranking = get_ranking_data(selected_coin_id)

#plot

if not df_ranking.empty:
    df_ranking['date']= pd.to_datetime(df_ranking['date'])
    
    plt.style.use('ggplot')
    fig, ax = plt.subplots()
    ax.plot(df_ranking['date'], df_ranking['mcr'], marker='o', markersize=2)
    ax.set_xlabel('Date')
    ax.set_ylabel('Market Cap Rank')
    ax.set_title(f'MCR over time for {selected_name}')
    ax.invert_yaxis()
    #rotate the x axis labels
    plt.xticks(rotation=90)

    st.pyplot(fig)
else:
    st.write("No data available for this coin")    
