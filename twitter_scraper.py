from asyncio.windows_events import NULL
from pickle import NONE
from time import time
from twitter_scraper_selenium import get_profile_details, scrape_profile
import json
import datetime as dt
import pytz
import sys
from pprint import pprint

def twit_data(handle):
    time_diff=9999
    followers_count = NULL
    try: 
        results = get_profile_details(twitter_username=handle)
        jresults = json.loads(results)
        followers_count = jresults["followers_count"]
    except:
        pass    

    if jresults and jresults["protected"] != True:


        try:
            tweets = scrape_profile(twitter_username=handle,output_format="json",browser="chrome",tweets_count=2)
            jtweets = json.loads(tweets)

            latest_time = None
            for tweet in jtweets.items():
                posted_time = dt.datetime.strptime(tweet[1]["posted_time"], '%Y-%m-%dT%H:%M:%S%z')
                if latest_time is None or posted_time > latest_time:
                    latest_time = posted_time    

            now = dt.datetime.now(pytz.utc)
            time_diff = (now - latest_time).days
        except:
            pass
    else: 
        followers_count = NULL   
    #time_diff is the number of days since the last tweet 
    return followers_count, time_diff
