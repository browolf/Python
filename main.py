import sys
sys.path.insert(0, './modules')

import sqlite3
from ping3 import ping
import datetime as dt
import time

"""
database construction 

CREATE TABLE "Devices" (
	"id"	INTEGER,
	"name"	TEXT,  
	"ip"	TEXT,
	"type"	INTEGER,
	PRIMARY KEY("id")
)

name  = device  name
type = S (Server), B(building), M(Misc)

CREATE TABLE "History" (
	"id"	INTEGER,
	"timestamp"	TEXT,
	"res"	REAL
)

res is either the ping time or NONE

"""


connection=sqlite3.connect('./databases/ping.db')
cursor = connection.cursor()

def myping(ip):
    return ping(ip)

def itemList(table):
    sql=("SELECT * from devices")
    cursor.execute(sql)
    return cursor.fetchall()

while True:
    today=dt.datetime.today()
    added=today.strftime("%Y-%m-%d-%H-%M")
    print(added)    

    for item in itemList("Devices"):
        res=myping(item[2])
        if isinstance(res, float): res=round(res,4)    
        cursor.execute(f"INSERT OR REPLACE INTO history('id','timestamp','res') values ('{item[0]}','{added}','{res}')")  
    connection.commit()
    time.sleep(60)      
