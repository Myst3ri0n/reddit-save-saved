import praw
import config as cfg
import re
import time
import urllib.request
import os
from gcore import db, timesys as t
import argparse
from requests_html import HTMLSession

start_time = time.time() 

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

d = db.DatabaseManager(db_name, False)

if new_db:
	d.query(d.readSql('install.sql'))

session = HTMLSession()

print('Downloading saved Reddit Images...\n')

reddit = praw.Reddit(client_id=cfg.client_id,
					client_secret=cfg.client_secret,
					password=cfg.password,
					user_agent=cfg.user_agent,
					username=cfg.username)

saved_posts = reddit.user.me().saved(limit=None)

post_info      = {}
album_count    = 0
url_count      = 1
for link in saved_posts:
	url      = link.url
	title    = link.title
	subr     = link.subreddit_name_prefixed[2:]
	perm_url = 'https://reddit.com'+link.permalink
	#filter out only images and gifs
	if url[-3:].upper() in ['JPG','PNG','GIF']:
		post_info[url_count] = {'Title':title,'Url':url,'Subreddit':subr,'Permalink':perm_url,'Is_Album':''}
		url_count+=1
	is_album = re.search(r'imgur\.com\/a\/',url)
	if is_album:
		print(f'{url} is an album...\n')
		r = session.get(url)
		r.html.render()
		album_html   = r.html.html
		album_images = re.findall(r'.*?{"hash":"([a-zA-Z0-9]+)".*?"ext":"(\.[a-zA-Z0-9]+)".*?',album_html)
		album_index  = 1
		for i in list(set(album_images)):
			img_id    = i[0]
			ext       = i[1]
			file_name = img_id+ext
			post_info[url_count] = {'Title':title+'_ALB_'+str(album_index),'Url':f'https://imgur.com/{img_id}{ext}','Subreddit':subr,'Permalink':perm_url,'Is_Album':'Y'}
			url_count+=1
			album_index+=1
		album_count+=1

post_keys = list(post_info.keys())

print(f'{album_count} albums detected...\n')

print(f'{len(post_keys)} images will be downloaded...\n')

#download files
for k in post_keys:
	title = post_info[k]['Title']
	url   = post_info[k]['Url']
	perm  = post_info[k]['Permalink']
	subr  = post_info[k]['Subreddit']
	alb   = post_info[k]['Is_Album']
	db_links = d.query("SELECT URL FROM DOWNLOAD_LOG;")
	if url in db_links and force==False:
		print(f'{title} already has been downloaded...')
		continue
	print(f'Downloading: {title}  ({url})')
	if not os.path.exists('saved/'+str(subr)) and folders:
		os.makedirs('saved/'+str(subr))
	file_name = re.search(r'(?=\w+\.\w{3,4}$).+',url).group(0)
	try:
		urllib.request.urlretrieve(url,'saved/'+subr+'/'+file_name if folders else 'saved/'+file_name)
		if url in db_links and force==True:
			d.query(f"""
				UPDATE 	DOWNLOAD_LOG
				SET 	DATE_DOWNLOADED = '{t.nowDateTime()}'
				WHERE 	URL='{url}';
					""")
		else:
			d.query(f"""
				INSERT INTO DOWNLOAD_LOG(USER,DATE_DOWNLOADED,URL,TITLE,SUB_REDDIT,PERMALINK,IS_ALBUM) 
				VALUES('{cfg.username}','{t.nowDateTime()}','{url}','{title}','{subr}','{perm}',{d.nullValue(alb)});
				""")
	except:
		print(f'Unable to download: ^^^{url}^^^')
	time.sleep(2)

time_took = round(time.time() - start_time,3)

print(f'\nProcess completed in {t.humanTime(time_took)}...')

print('\nProcess Complete!\n')