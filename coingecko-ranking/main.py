import requests
import sqlite3
import time
import datetime as dt

today=dt.date.today()
added = today.strftime("%Y-%m-%d")

con = sqlite3.connect("data.db")
cursor = con.cursor()

request = requests.get("https://api.coingecko.com/api/v3/coins/list")
coins = request.json()

req_counter = 1

for coin in coins:
 
    print(coin["name"])

    #check if coin has been updated
    sql = f"""select updated from coins where id="{coin['id']}" """
    cursor.execute(sql)
    res = cursor.fetchone()
    if res[0]:
        continue  


    print(coin)    
    cursor.execute(f"""INSERT OR IGNORE into coins (id,symbol,name) values ("{coin['id']}","{coin['symbol']}","{coin['name']}")""")

    
    #calculate age
    request = requests.get(f"""https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={coin['id']}&order=market_cap_desc&per_page=100&page=1&sparkline=false""")
    data = request.json()
    req_counter+=1
    try:
        atl=dt.datetime.fromisoformat(data[0]['atl_date'].replace('Z', '+00:00')).date()
        ath=dt.datetime.fromisoformat(data[0]['ath_date'].replace('Z', '+00:00')).date()
        age = (today-(min(ath,atl))).days
    except:
        age = "-"

    while True:
        try:    
            #fetch individual coin data
            request = requests.get(f"https://api.coingecko.com/api/v3/coins/{coin['id']}?localization=false&tickers=false&market_data=false&community_data=true&developer_data=true&sparkline=false")
            data = request.json()
            req_counter+=1
            sql=(f"""INSERT OR REPLACE into coins
                        (id,
                        symbol,
                        name,
                        categories,
                        twitter,
                        genesis,
                        mcr,
                        coingecko_rank,
                        coingecko_score,
                        developer_score,
                        community_score,
                        public_interest_score,
                        total_score,
                        alexa,
                        age,
                        updated) 
                values ("{coin['id']}",
                    "{coin['symbol']}",
                    "{coin['name']}",
                    "{','.join(data['categories'])}",
                    "{data['links']['twitter_screen_name']}",
                    "{data['genesis_date']}",
                    "{data['market_cap_rank']}",
                    "{data['coingecko_rank']}",
                    "{data['coingecko_score']}",
                    "{data['developer_score']}",
                    "{data['community_score']}",
                    "{data['public_interest_score']}",
                    "{data['coingecko_score']+data['developer_score']+data['community_score']+data['public_interest_score']}",
                    "{data['public_interest_stats']['alexa_rank']}",
                    "{age}",
                    "{added}")
                    """)
        except:
            print(f".. {req_counter}..sleeping")
            time.sleep(30)
            continue
        else:
            break
    
    cursor.execute(sql)
    print(f"Done {coin['name']}......{req_counter}")
    con.commit()
    #sys.exit()
    if req_counter >= 30:
        print(".............Taking a break!")
        time.sleep(27)
        req_counter=0
    time.sleep(3)

