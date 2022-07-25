from app import app
import datetime as dt
import sqlite3
from flask import url_for


@app.route('/')
@app.route('/index')

def index():

    def buildRow(dfList):
        #split the list of lists into 2 lists
        iName = [x[0] for x in dfList]
        iRes = [x[2] for x in dfList]
        #start row
        newstr=("<tr>\n")
        #for each device
        for item in iName:
            #put the name in a cell will a blank cell next to it                   
            newstr+=(f"<td cellpadding='4'><p>{item}</p></td><td cellpadding='4'>&nbsp;&nbsp;&nbsp;&nbsp;</td>")
        #end row    
        newstr+=("</tr>\n\n<tr>\n\n")    
        #for each device result
        for item in iRes:
            #find out cell colour
            col = "red" if item=="None" else "green"
            #find out  if there's time label
            label = "<br style='visibility:hidden'>" if item=="None" else item 
            #write result cell and a blank cell next to it 
            newstr+=(f"<td cellpadding='4' bgcolor='{col}'><center>{label}</center></td><td cellpadding='4'>&nbsp;&nbsp;&nbsp;&nbsp;</td>")  
        newstr+=("</tr><tr></tr>\n")
        return newstr 

    today=dt.datetime.today()
    thistime=today.strftime("%Y-%m-%d %H:%M")

    #connect db
    connection=sqlite3.connect('././databases/ping.db')
    cursor = connection.cursor()
    #fetch the hierachy levels
    cursor.execute(f"select * from hierarchy")
    levels=[item for item in cursor.fetchall()]

    #process start table

    htmlstr=""
    for level in levels:
        #title
        htmlstr+=(f"<h2>{level[1]}</h2>\n")
        #create new table
        htmlstr+=("<table>\n\n")
        #for this level fetch devices
        cursor.execute(f"""
        select devices.name,devices.level, current.res from Devices
            inner join current on devices.id=current.id
	        where devices.level='{level[0]}'
        """)
        devices=[device for device in cursor.fetchall()]
        #build rows(s) for this level
        htmlstr+=buildRow(devices)
        #end table
        htmlstr+=("</table>\n\n")

    

    return f"""
    
    <html>
        <head>
            <title>LSA  Uptime Monitor</title>
            <meta http-equiv='refresh' content='60' />
            <link rel="stylesheet" href="{url_for('static', filename='css/main.css')}">
            <link rel="stylesheet" type="text/css" href="//fonts.googleapis.com/css?family=Shanti" />
        </head>

        <body>
            <center><h1>LSA Uptime Monitor</h1></center>
            <center><p>Time: {thistime}</p></center>
            <p>
            <center>
            {htmlstr}
            <center>

    
    
    
    
    """
