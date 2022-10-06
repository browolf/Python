from flask import Flask, url_for, render_template, request
import datetime as dt
import socket
import os

#Config options=======================================================
#device names and IPs do not represent real devices. 
levels = [(1, 'Core'), (2, 'Hosts'), (3, 'Servers'), (4, 'Buildings')]
#Name, ip, port, level
devices = [('Dc', '10.7.7.1', 3389, 3), ('Dc', '10.7.7.1', 3389,  3), ('Newt', '10.7.7.1', 22,  4), ('Music', '10.7.7.1', 22,  4), ('Science', '10.7.7.1', 22,  4), ('Sync', '10.7.7.1', 3389,  3), ('Develop', '10.7.7.1', 3389,  3), ('Imaging', '10.7.7.1', 22,  3), ('Term01', '10.7.7.1', 3389,  3), ('VPN', '10.7.7.1', 22,  3), ('Hyworks', '10.7.7.1', 3389,  3), ('catering', '10.7.7.112', 3389,  3), ('Solidworks', '10.7.7.1', 3389,  3), ('Core01', '10.7.7.1', 22,  1), ('Internet', '8.8.8.8', 53,  1), ('Core02', '10.7.7.1', 22,  1), ('ESX1', '10.7.7.1', 80,  2), ('Esx2', '10.7.7.1', 80,  2), ('HPSan', '10.7.7.1', 443,  2), ('Print', '10.7.7.1', 3389,  3), ('Pupils', '10.7.7.1', 3389,  3), ('Sql', '10.7.7.1', 3389,  3), ('Staff', '10.7.7.1', 3389,  3), ('Ubiq', '10.7.7.1', 22,  3), ('Ups1', '10.7.7.1', 22,  3), ('Vmw', '10.7.7.1', 22,  3), ('Voicebox', '10.7.7.1', 3389,  3), ('Screens', '10.7.7.1', 22,  3), ('Main', '10.7.7.1', 22,  4), ('ICT', '10.7.7.1', 22,  4), ('DT', '10.7.7.1', 22,  4), ('StuServ', '10.7.7.1', 22,  4), ('PE', '10.7.7.1', 80,  4), ('test', '10.7.7.119', 1234,  4)]
#ipaddress of server running script. 
IPAddr="10.7.7.15"
school="My School"
#====================================================================


#reset iteration counter
iteration_counter=0


template_dir = os.path.abspath('./')
app = Flask(__name__, template_folder=template_dir)
app.debug=True

@app.route('/', methods=['GET', 'POST'])
def index():
    global iteration_counter
    htmlstr=""

    #determine device - used to determine 
    user_agent = request.headers.get("User-Agent").lower()
    cells = 10 if "windows" in user_agent else 2
    print(f"{user_agent} + {cells}")

    def test_port(a,p):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex((a,p))
        return False if result else True   

    def build_table(dfList,c):
        #c is the max number of cells per row. You want less on a phone
        def buildCell(name,result):
            col = "red" if result == False else "#C4D79B" 
            return f"<table><tr><td>{name}</td><td>&nbsp;</td></tr>\n<tr><td bgcolor='{col}'> </td><td>&nbsp;</td></tr></table>\n"
        newstr=""
        #create new table
        newstr+=("<table>\n<tr>\n")
        cellcount=1
        for item in dfList:
            newstr+=("<td><center>")
            name=item[0]
            res=item[1]
            newstr+=buildCell(name,res)
            if cellcount==c:
                newstr+=("</tr><tr>")
                cellcount=0
            cellcount+=1   
            newstr+=("<center></td>") 
        newstr+=("</tr>\n</table>\n\n")
        return newstr 

    for level in levels:      
        #title
        htmlstr+=(f"<h2>{level[1]}</h2>\n")
        device_results=[]
        filtered_devices = [tup for tup in devices if tup[3]==level[0]]
        for device in filtered_devices:
            result = test_port(device[1],device[2])
            device_results.append([device[0],result])

        htmlstr+=build_table(device_results,cells)
    iteration_counter+=1
    return render_template('index.html', htmlstr=htmlstr, iter=iteration_counter, school=school)




if __name__ == '__main__':
    app.run(IPAddr,5001)  
