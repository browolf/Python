import os
import time
import sys
import key as key
import openai
from authenticate import redditAuthenticate

"""
This bot provides comments by chatgpt in the relationship advice sub
"""

openai.api_key = key.api_key
reddit = redditAuthenticate()

sub= "relationship_advice"

def xtime():
    t = time.localtime()
    return time.strftime("%Y/%m/%d %H:%M:%S", t)

def checksub(subname):
    subreddit = reddit.subreddit(subname)
    print(xtime() + " " + subname + "\n")
    for submission in subreddit.new(limit=100):
        if submission.id not in posts_replied_to:
            print(f"ID: {submission.id} Length: {len(submission.selftext)}")
            response = openai.Completion.create(
            model = "text-curie-001",
            prompt = text,
            max_tokens = 500)
            print(response)
            try:
                submission.reply(response.choices[0].text)
            except Exception as e: 
                print(f"Error: {e}")
            else:    
                print(submission.title)
                #posts_replied_to.append(submission.id)
            


while True:
    if not os.path.isfile("posts_replied_to.txt"):
        posts_replied_to=[]
    else:
        with open("posts_replied_to.txt") as f:
              posts_replied_to = f.read()
              posts_replied_to = posts_replied_to.split("\n")
              posts_replied_to = list(filter(None, posts_replied_to))
    checksub(sub)


    with open("posts_replied_to.txt", "w") as f:
        for post_id in posts_replied_to:
            f.write(post_id + "\n")
            print(post_id)
    sys.exit()        
    time.sleep(500)                   
