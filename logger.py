#super simple logger 
#usage:
#import logger
#logger.log("something happened")
#logger.closef

import datetime
import __main__

logfile=open("{f}.log".format(f=__main__.__file__),"a")

def log(str):
    timestamp = datetime.datetime.now()
    logfile.write("{time}: {str}\n".format(time=timestamp.strftime("%Y-%b-%d %H%M"),str=str))

def closef():
    logfile.close()
