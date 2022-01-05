import subprocess
import sys
import re

f=open("output.csv","w")

servers=["server01","server02","server03"]
def run(cmd):
    completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True,text=True)
    return completed

for server in servers:
    cmdline="GWMI -computername {s} -namespace root\cimv2 -class win32_volume | FL -property DriveLetter, DeviceID".format(s=server)
    res=run(cmdline)
    #print(res.stdout)
    #print(type(guid))
    guid2=re.split("Volume",guid[0])
    
    print ("{s},{g}".format(g=guid2[1],s=server))   
    f.write("{s},{g}\n".format(g=guid2[1],s=server))
