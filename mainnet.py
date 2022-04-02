from urllib import request as urlrequest
import ssl
import json
import sys
import sqlite3
import time

connection=sqlite3.connect("mainnet.db")
cursor = connection.cursor()

def get_json(url):
   req = urlrequest.Request(url)
   req.set_proxy('10.77.32.83:3128', 'http')
   gcontext = ssl.SSLContext()
   error_hap=False
   while True:
      try:
         response = urlrequest.urlopen(req,context=gcontext)
      except:
         print(f"Error sleeping - URL={url}")
         error_hap=True
         time.sleep(60)
         pass
      else:
         if error_hap: 
            print("Continuing...")
         break
   res=response.read().decode('utf8')
   jres=json.loads(res)
   return jres


jurl=get_json("https://api.mainnet.minepi.com/")
latest_ledger=jurl['core_latest_ledger']

def initialize_database():
   print("Initalizaing Database")
   cursor.execute("""CREATE TABLE IF NOT EXISTS age (
      id INTEGER,
      cnt INTEGER DEFAULT 0);""")   
   cursor.execute("insert into age (id,cnt) values (1,0)")
   connection.commit()

#check if table exists
cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='age'")
if cursor.fetchone()[0] !=1:
   initialize_database()

#read values
cursor.execute("select * from age")
db_res=cursor.fetchone()
start_ledger=db_res[0]
count=db_res[1]

print(f"start:{start_ledger} count:{count}")



for ledger_id in range(start_ledger+1,latest_ledger):
   #fetch ledger
   ledger=get_json(f"https://api.testnet.minepi.com/ledgers/{ledger_id}/operations")

   if len(ledger['_embedded']['records']) > 0: 
      #not empty
      record_array=ledger['_embedded']['records']
      for record in record_array:
         if record['type'] == "create_account":
            count=count+1
            cursor.execute(f"update age set id='{ledger_id}', cnt={count}")
            print(f"Ledger {ledger_id} Op_id:{record['id']} cnt={count}") 
            #sys.exit()
            if int(count)%100 == 0:
               connection.commit()
               print(f"committed at Count:{count}")      
   else:
      #just update ledgerid
      cursor.execute(f"update age set id='{ledger_id}'")
      if int(ledger_id)%100 == 0:
         connection.commit()
         print(f"committed at Ledger:{ledger_id}")  
      #connection.commit()   
      #print(f"{ledger_id} not empty")
      #sys.exit()

