import sqlite3
import pandas as pd

con = sqlite3.connect("data.db")
cursor = con.cursor()

sql="select coingecko_rank,name,mcr,coingecko_score from coins order by coingecko_score desc limit 50"

cursor.execute(sql)

df=pd.DataFrame(cursor.fetchall(),columns=['CGRank','Name','MarketCapRank','CGScore'])





print(df)
df.to_csv('results.csv', index=False)  