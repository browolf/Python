"""
This script flood fake wallet passphase stealing sites with newly generated passphrases
"""
from mnemonic import Mnemonic
from urllib.request import Request,urlopen
import json
import random
import requests
import sys
import time

#memo = Mnemonic(language)
def get_memo():
    memo = Mnemonic("english")
    words = memo.generate(strength=256)
    seed = memo.to_seed(words, passphrase="")
    #words2=words.replace(" ","+")
    return words

def get_proxy():
    hdrs = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36"
    }
    url="https://proxylist.geonode.com/api/proxy-list?limit=50&page=1&sort_by=lastChecked&sort_type=desc"
    req = Request(url, headers=hdrs)
    res = urlopen(req).read()
    jres=json.loads(res)   
    proxies=[]
    for item in jres["data"]:
        proxies.append(f"{item['ip']}:{item['port']}")
    return random.choice(proxies)    
    

while True:
    proxies = {"http": get_proxy()}
    hdrs= {
        "Host": "piblock.onrender.com",
        "Connection": "keep-alive",
        "Accept": "*/*",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type",
        "Origin": "http://pinetworkblockchain.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Dest": "empty",
        "Referer": "http://pinetworkblockchain.com/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-GB-oxendict,en;q=0.9",

    }

    url="https://piblock.onrender.com/message"
    myobj = {
    "message" : get_memo()}
    print(f"{url}\n {proxies}\n {myobj}\n")
    try:
        print("try1")
        res1 = requests.post(url, proxies=proxies, data="",  headers=hdrs)
        print(res1.content)
        res2 = requests.post(url, proxies=proxies,  data=myobj, headers=hdrs)
        print(res2.content)
    except Exception as e:
        print(f"Some kind of Error: {e}")
        pass
    else:
        print("Done?")
        
    time.sleep(60)


