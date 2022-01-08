import datetime
import __main__

#import logger
#logger.log("something happened")


def log(str):
    timestamp = datetime.datetime.now()
    with open(f"{__main__.__file__}.log","a") as file:
        file.write(f"{timestamp.strftime('%Y-%b-%d %H%M')}: {str}\n")


