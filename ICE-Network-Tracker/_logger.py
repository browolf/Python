import datetime
import __main__

#import logger
#logger.log("something happened", optional "Y" for print)

"""
It's a super basic logger - the destination file is the mainscript.py.log
"""

def log(str,pr="N"):
    str=str.replace("\n","")
    timestamp = datetime.datetime.now()
    with open(f"{__main__.__file__}.log","a") as file:
        file.write(f"{timestamp.strftime('%Y-%b-%d %H%M')}: {str}\n")
    if pr == "Y": 
        print(str)    
