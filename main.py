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

#filter out only images and gifs
links = []
title = []
for link in saved_posts:
	if link.url[-3:].upper() in ['JPG','PNG','GIF']:
		title.append(link.title)
		links.append(link.url)

print(f'{len(links)} images will be downloaded...\n')

#download files
index = 0
for l in links:
	url = l
	print(f'Downloading: {title[index]}  ({url})')
	file_name = re.search(r'(?=\w+\.\w{3,4}$).+',url).group(0)
	urllib.request.urlretrieve(url,'saved/'+file_name)
	time.sleep(2)
	index+=1

print('\nProcess Complete!')