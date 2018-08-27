import praw
import config as cfg
import re
import time
import urllib.request

print('Downloading all saved Reddit Images...\n')

reddit = praw.Reddit(client_id=cfg.client_id,
                     client_secret=cfg.client_secret,
                     password=cfg.password,
                     user_agent=cfg.user_agent,
                     username=cfg.username)

saved_posts = reddit.user.me().saved(limit=None)

for l in saved_posts:
	url = l.url
	print('Downloading: '+url)
	file_name = re.search(r'(?=\w+\.\w{3,4}$).+',url).group(0)
	urllib.request.urlretrieve(url,'saved/'+file_name)
	time.sleep(2)

print('\nProcess Complete!')