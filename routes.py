from numpy import newaxis
from app import app
import datetime as dt
import sqlite3
import pandas as pd


@app.route('/')
@app.route('/index')


def index():
    #connect db
    connection=sqlite3.connect('././databases/ping.db')
    cursor = connection.cursor()
    #it needs to fetch 1 before latest timestamp
    cursor.execute("select DISTINCT timestamp from history order by timestamp desc limit 2")
    thistime=cursor.fetchall()[1][0]
    
    #fetch results for all devices
    cursor.execute(f"""
    select devices.name,devices.type, history.res from Devices
    inner join history on devices.id=history.id
    where history.timestamp='{thistime}'""")

    #use a dataframe to filter the types
    df=pd.DataFrame(cursor.fetchall())
    df.columns=['Name','Type','Result']
    servers=df[df['Type']=='S']
    buildings=df[df['Type']=='B']
    misc=df[df['Type']=='M']
    
    #process each df into html

    htmlstr="""
        <table>\n\n

    """

    def buildRow(dfList):
        iName = [x[0] for x in dfList]
        iRes = [x[2] for x in dfList]
        newstr="<tr>\n"
        for item in iName:                   
            newstr+=f"<td cellpadding='2'>{item}</td><td></td>"
        newstr+="</tr>\n\n<tr>\n\n"    
        for item in iRes:
            col = "red" if item=="None" else "green"
            label = "" if item=="None" else item 
            newstr+=f"<td bgcolor='{col}'>{label}</td><td></td>"  
        newstr+="</tr><tr></tr>\n"
        return newstr             

    for df2 in [servers,buildings,misc]:
        #print(f"DF2 = {df2}\n\n")
        #max number of items in row =?

        #start row
        #print(f"THIS LIST ITEMS = {items}\n\n")
        htmlstr+=buildRow(df2.values.tolist())
        
        #print(items)

    htmlstr+="""
        </table>\n\n
    """

    return f"""
    
    <html>
        <head>
            <title>LSA  Uptime Monitor</title>
             <meta http-equiv='refresh' content='60' />
        </head>

        <body>
            <center><h1>LSA Uptime Monitor</h1></center>
            <h2>Time: {thistime}</h2>
            <p>
            {htmlstr}

    
    
    
    
    """