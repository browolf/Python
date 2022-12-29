import os
import time
import sys
from webbrowser import get
import key as key
import openai
from authenticate import redditAuthenticate

"""
This bot fetches posts from a given subreddit and reposts them on another subreddit with a comment from chatgpt
"""


openai.api_key = key.api_key

reddit = redditAuthenticate()
#subname = "openaibot"
subname = "relationship_advice"

def xtime():
    t = time.localtime()
    return time.strftime("%Y/%m/%d %H:%M:%S", t)

def load_replied_to():
    if not os.path.isfile("posts_replied_to.txt"):
        posts_replied_to=[]
    else:
        with open("posts_replied_to.txt") as f:
              posts_replied_to = f.read()
              posts_replied_to = posts_replied_to.split("\n")
              posts_replied_to = list(filter(None, posts_replied_to))
    return posts_replied_to             


def get_newposts(sub):
    subreddit = reddit.subreddit(sub)
    post_list=[]
    for submission in subreddit.new(limit=1):
        post_list.append(submission)
    return post_list    
    
def askai(question): 
    print(f"Len: {len(question)}")  
    response = openai.Completion.create(
    model = "text-curie-001",
    prompt = question,
    max_tokens = 500)
    #print(response)
    return response.choices[0].text,response.id   

def post_original(original_post_object):
    post_sub =  reddit.subreddit("relationship_adviceAI")
    title = original_post_object.title
    if original_post_object.selftext:
        try:
            body = (f"{original_post_object.url}\n\n {original_post_object.selftext}")
            new_post_object = post_sub.submit(title, selftext=body)                      
        except Exception as e:
            print(f"Error: {e} posting {title}")
        else:
            #approve post
            #approve_submission(new_post_object)
            checklist.append(original_post_object.id)
            return new_post_object

def reply_to_post(post_object,ai_response,id):
    try:
        #reply to post
        body = ai_response + "\n\n" + f"ID:{id}" + "\n\nModel: text-curie-001" 
        the_post = reddit.submission(post_object.id)
        comment = the_post.reply(body)
    except Exception as e:
        print(f"Error {e} : posting reply ")
    else:
        print(f"Success for {post.title}")
        #approve_submission(comment)

while True:
    #1 load posts_replied_to
    checklist = load_replied_to()
    print(f"Checklist aka posts replied to: {checklist}")
    #2 get a list of new post
    post_list = get_newposts(subname)
    print(f"PostList: {post_list}")
    #3check if already replied to or not
    for post in post_list:
        if post.id not in checklist:
            new_post = post_original(post)
            if new_post:
                try:
                    #print("would fetch answer")
                    answer,answer_id = askai("\n What do you think about this: " + post.selftext + "\n")   
                except Exception as e:
                    print(f"Error getting answer from chatgpt for {post.title}")       
                else:
                    reply_to_post(new_post,answer,answer_id)
                    pass    
            else:
                print("Reposting failed") 
        else:
            print("Nothing to do!")

    #4 update posts file
    with open("posts_replied_to.txt", "w") as f:
        for post_id in checklist:
            f.write(post_id + "\n")
            #print(f"Recorded {post_id}")   

    #sys.exit()
    time.sleep(500)
