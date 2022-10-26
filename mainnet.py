#this scripts counts the create_account operations per ledger and keeps track of the number so you can stop and start the script.

import sqlite3
import os
import socket
import sys
from urllib import request as urlrequest
import ssl
import time
import json
import re
import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning
from pprint import pprint as pp

HEADER = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36' }


def initialize_database():
  print("Initalizaing Database")
  lcursor.execute("""CREATE TABLE IF NOT EXISTS age (
    id INTEGER,
    cnt INTEGER DEFAULT 0);""")   
  lcursor.execute("insert into age (id,cnt) values (2,1)")
  connection.commit()

#progress storage DB
connection=sqlite3.connect("mainnet.db")
lcursor = connection.cursor()

#check if table exists
lcursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='age'")
if lcursor.fetchone()[0] !=1:
  initialize_database()   

def get_json(url):
  headers = requests.utils.default_headers()
  headers.update = ( HEADER,)
  proxy = {'https' : 'http://10.77.32.83:3128'}
  e = False
  
  while True:
    try:
      with warnings.catch_warnings():
        warnings.simplefilter('ignore', InsecureRequestWarning)
        response = requests.get(url, headers=headers, proxies=proxy, verify=False)
    except Exception as err:
      print(f"Error Sleeping - URL = {url} \n{err}")
      e = True
      time.sleep(60)
      pass
    else:
      if e:
        print("continuing...")
      break
  res=response.text
  jres=json.loads(res) 
  time.sleep(1)
  return jres

#remote update
def updateDB(id,c,lat):
   #c=count, lat=ledger
  url=(f"http://www.domain.com/insert.php?network=mainnet&id={id}&c={c}&lat={lat}")
  try: 
    response = requests.get(url, headers=HEADER)
  except Exception as err:
    print(f"Remote url: {url}")
    print(f"Error: {err}")
  else: 
    print(f"Remote Commit: {response.text}")

#read initial values
#read values
lcursor.execute("select * from age")
db_res=lcursor.fetchone()
current=db_res[0]
count=db_res[1]
cursor=""
print(f"Continuining at ledger #{current} count={count}")

#get dictionary for a ledger page and the nextpage cursor
def get_page(b,c=""):
    page=get_json(f"https://api.mainnet.minepi.com/ledgers/{b}/operations?limit=200&cursor={c}")
    ncursor=re.search(r"\d{15,20}",page["_links"]["next"]["href"]) 
    return page,ncursor.group()

#count operations in dictionary,
#return last cursor as well
def count_ops(p):
    this_page_count=0
    for record in p['_embedded']['records']: 
        if record['type'] == "create_account":
            this_page_count+=1
    return this_page_count 


while True:

  current+=1
  print(f"MN: {current}")
  #Update DB + Commit (need to check before continues)
  if current%100==0:
    lcursor.execute(f"update age set id={current}, cnt={count}")
    connection.commit()
    updateDB(current,count,latest) 
    print(f"commiting changes at ledger:{current} cnt={count}")

  #get latest ledger id
  latest=get_json("https://api.mainnet.minepi.com/")['core_latest_ledger']
  #sleep if caught up
  if current == latest:
    print("Caught Up - Sleeping")
    time.sleep(300)
    continue

  #get number of operations in current ledger 
  try:
    operations=get_json(f"https://api.mainnet.minepi.com/ledgers/{current}")['operation_count']
  except KeyError:
    print("KeyError")
    pp(current)
    pp(operations)
    sys.exit() 
  
  if operations > 400: 
    print("Operations more than 400 detected..exiting")
    sys.exit() 
  elif operations == 0:
    continue

  #reset local count
  thiscount=0 

  if operations > 0:
    #how many pages
    pages=int((operations/200))+1  

    #get first page
    ledger,cursor=get_page(current)
    #count ops first page
    thiscount=count_ops(ledger)
    
    #count ops in extra pages
    if pages > 1:
        for _ in range(2,pages+1):
            ledger,cursor=get_page(current,cursor)
            ops=count_ops(ledger)
            thiscount+=ops
            if thiscount > 200:
              print("Killswitch thiscount>200 need to check")
              sys.exit()
    count+=thiscount

    print(f"---------pages={pages} OPS={operations},countedOPS={thiscount}, total={count}")

#the 200 killswitch was at 335000/ start for 2 ops
