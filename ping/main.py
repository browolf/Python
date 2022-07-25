import sys
sys.path.insert(0, './modules')

import sqlite3
from ping3 import ping
import datetime as dt
import time

"""
database construction 

CREATE TABLE "hierarchy" (
	"id"	INTEGER,
	"name"	TEXT,
	PRIMARY KEY("id")
)

Hierarchy is a series of levels displayed on the webpage. 
These will be: Core, Servers, Buildings, Misc

CREATE TABLE "Devices" (
	"id"	INTEGER,
	"name"	TEXT,
	"ip"	TEXT,
	"level"	INTEGER,
	PRIMARY KEY("id")
)

CREATE TABLE "History" (
	"id"	INTEGER,
	"timestamp"	TEXT,
	"res"	REAL
)

CREATE TABLE "Current" (
	"id"	INTEGER,
	"res"	TEXT,
	PRIMARY KEY("id")
)

current is overwritten with the current ping results of each device

"""


connection=sqlite3.connect('./databases/ping.db')
cursor = connection.cursor()

def myping(ip):
    return ping(ip)

def itemList(table):
    sql=("SELECT * from devices")
    cursor.execute(sql)
    return cursor.fetchall()


#pings each device in turn and writes a historical record and a current record
while True:
    today=dt.datetime.today()
    added=today.strftime("%Y-%m-%d-%H-%M")
    print(added)    
    for item in itemList("Devices"):
        res=myping(item[2])
        if isinstance(res, float): res=round(res,4)    
        cursor.execute(f"INSERT OR REPLACE INTO history('id','timestamp','res') values ('{item[0]}','{added}','{res}')")  
        cursor.execute(f"INSERT OR REPLACE INTO current('id','res') values ('{item[0]}','{res}')")  
    connection.commit()
    time.sleep(60)      
