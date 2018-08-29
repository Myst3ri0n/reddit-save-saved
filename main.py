import praw
import config as cfg
import re
import time
import urllib.request
import os
import gcore as g
import argparse
from requests_html import HTMLSession

parser = argparse.ArgumentParser()
parser.add_argument('--force',action='store_true')
parser.add_argument('--folders',action='store_true')
parser = parser.parse_args()

force    = parser.force
folders  = parser.folders

db_name='saved'

new_db = False
if os.path.isfile(db_name+'.db') == False:
	new_db = True

d = g.db.DatabaseManager(db_name, False)

if new_db:
	d.query(d.readSql('install.sql'))

session = HTMLSession()

print('Downloading all saved Reddit Images...\n')

reddit = praw.Reddit(client_id=cfg.client_id,
					client_secret=cfg.client_secret,
					password=cfg.password,
					user_agent=cfg.user_agent,
					username=cfg.username)

saved_posts = reddit.user.me().saved(limit=None)

#filter out only images and gifs
links       = []
titles      = []
subreddit   = []
album_count = 1
for link in saved_posts:
	url   = link.url
	title = link.title
	subr  = link.subreddit_name_prefixed[2:]
	if url[-3:].upper() in ['JPG','PNG','GIF']:
		titles.append(title)
		links.append(url)
		subreddit.append(subr)
	is_album = re.search(r'imgur\.com\/a\/',url)
	if is_album:
		print(url+' is an album...\n')
		r = session.get(url)
		r.html.render()
		album_html   = r.html.html
		album_images = re.findall(r'.*?{"hash":"([a-zA-Z0-9]+)".*?"ext":"(\.[a-zA-Z0-9]+)".*?',album_html)
		album_index  = 1
		for i in list(set(album_images)):
			img_id    = i[0]
			ext       = i[1]
			file_name = img_id+ext
			album_url = f'https://imgur.com/{img_id}{ext}'
			links.append(album_url)
			titles.append(title+'_ALB_'+str(album_index))
			subreddit.append(subr)
			album_index+=1

		album_count+=1

print(f'{album_count} albums detected...\n')

print(f'{len(links)} images will be downloaded...\n')

#download files
index = 0
for l in links:
	db_links = d.query("SELECT URL FROM DOWNLOAD_LOG;")
	if l in db_links and force==False:
		print(f'{titles[index]} already has been downloaded...')
		index+=1
		continue
	url = l
	print(f'Downloading: {titles[index]}  ({url})')
	if not os.path.exists('saved/'+str(subreddit[index])) and folders:
		os.makedirs('saved/'+str(subreddit[index]))
	d.query(f"INSERT INTO DOWNLOAD_LOG(USER,URL,TITLE,SUB_REDDIT) VALUES('{cfg.username}','{url}','{titles[index]}','{subreddit[index]}');")
	file_name = re.search(r'(?=\w+\.\w{3,4}$).+',url).group(0)
	try:
		urllib.request.urlretrieve(url,'saved/'+subreddit[index]+'/'+file_name if folders else 'saved/'+file_name)
	except:
		print(f'Unable to download: ^^^{url}^^^')
	time.sleep(2)
	index+=1

print('\nProcess Complete!')