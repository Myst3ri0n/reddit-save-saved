import praw
import config as cfg
import re
import time
import os
import datetime
import argparse
import shutil
from urllib.request import Request, urlopen
from termcolor import colored, cprint
from gcore import db, timesys as t
from requests_html import HTMLSession

start_time = time.time() 

parser = argparse.ArgumentParser()
parser.add_argument('--force',action='store_true')
parser.add_argument('--folders',action='store_false')
parser = parser.parse_args()

force    = parser.force
folders  = parser.folders

db_name='saved'

new_db = False
if os.path.isfile(db_name+'.db') == False:
	new_db = True

d = db.DatabaseManager(db_name, False)

db_file_size = os.stat('saved.db').st_size

if new_db or db_file_size==0:
	d.query(d.readSql('install.sql'))

d.query(f"INSERT INTO JOB_TRACKER(START_DATE) VALUES('{t.nowDateTime()}');")
job_id = d.query('SELECT ID FROM JOB_TRACKER ORDER BY ID DESC LIMIT 1;',fo=True)

session = HTMLSession()

print('Downloading saved Reddit Images...\n')

reddit = praw.Reddit(client_id=cfg.client_id,
					client_secret=cfg.client_secret,
					password=cfg.password,
					user_agent=cfg.user_agent,
					username=cfg.username)

saved_posts = reddit.user.me().saved(limit=None)

post_info       = {}
album_count     = 0
url_count       = 1
album_img_count = 0
for link in saved_posts:
	user      = link.author
	url       = link.url
	title     = link.title
	subr      = link.subreddit_name_prefixed[2:]
	perm_url  = 'https://reddit.com'+link.permalink
	post_time = datetime.datetime.fromtimestamp(link.created)
	up_votes  = link.ups
	#filter out only images and gifs
	if url[-3:].upper() in ['JPG','PNG','GIF']:
		file_name = re.findall(r'(?=\w+\.\w{3,4}$).+',link.url)[0]
		post_info[url_count] = {'User':user,'Title':title,'Url':url,'File_Name':file_name,
								'Album_Url':'','Subreddit':subr,'Permalink':perm_url,
								'Is_Album':'','Alb_Index':'','Post_Time':post_time,
								'Up_Votes':up_votes}
		url_count+=1
	is_album = re.search(r'imgur\.com\/a\/',url)
	if is_album:
		print(f'Scanning Album: {title[:80]} ({url})...\n')
		r = session.get(url+'/layout/blog')
		album_html   = r.html.html
		album_images = re.findall(r'.*?{"hash":"([a-zA-Z0-9]+)".*?"ext":"(\.[a-zA-Z0-9]+)".*?',album_html)
		album_index  = 1
		for i in list(set(album_images)):
			img_id    = i[0]
			ext       = i[1]
			file_name = img_id+ext
			post_info[url_count] = {'User':user,'Title':title+'_ALB_'+str(album_index),
									'Url':f'https://imgur.com/{img_id}{ext}','File_Name':img_id+ext,
									'Album_Url':url,'Subreddit':subr,'Permalink':perm_url,'Is_Album':'Y',
									'Alb_Index':album_index,'Post_Time':post_time,'Up_Votes':up_votes}
			url_count+=1
			album_index+=1
			album_img_count+=1
		album_count+=1

post_keys = list(post_info.keys())

print(f'{album_count} albums detected with {album_img_count} images...\n')

print(f'{len(post_keys)} total images will be downloaded...\n')

time.sleep(5)

download_count = 0
current_count  = 1

#download files
for k in post_keys:
	user      = post_info[k]['User']
	title     = post_info[k]['Title']
	url       = post_info[k]['Url']
	alb_url   = post_info[k]['Album_Url']
	perm      = post_info[k]['Permalink']
	subr      = post_info[k]['Subreddit']
	alb       = post_info[k]['Is_Album']
	alb_i     = post_info[k]['Alb_Index']
	file_name = post_info[k]['File_Name']
	post_time = post_info[k]['Post_Time']
	up_votes  = post_info[k]['Up_Votes']
	db_links  = d.query("SELECT URL FROM DOWNLOAD_LOG;")
	if url in db_links and force==False:
		print(f'{title} already has been downloaded...')
		current_count += 1
		continue
	print(f'Downloading: {title[:80]}  ({url}) :: {str(current_count)} out of {str(len(post_keys))}')
	current_count += 1
	if not os.path.exists('static/saved/'+str(subr)) and folders:
		os.makedirs('static/saved/'+str(subr))
	file_name = re.search(r'(?=\w+\.\w{3,4}$).+',url).group(0)
	save_location = f'static/saved/{subr}/{file_name}' if folders else f'static/saved/{file_name}'
	try:
		req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
		with urlopen(req) as response, open(save_location, 'wb') as out_file:
			shutil.copyfileobj(response, out_file)
		if url in db_links and force==True:
			d.query(f"""
				UPDATE 	DOWNLOAD_LOG
				SET 	DATE_DOWNLOADED = '{t.nowDateTime()}'
				WHERE 	URL='{url}';
					""")
		else:
			#determining if image is missing form imgur
			if urlopen(url).geturl()=='https://i.imgur.com/removed.png':
				error_msg = 'Imgur Missing Image.'
				cprint(f'Unable to download: ^^^{url}^^^ The error was: Imgur Missing Image.','red', 'on_cyan',attrs=['bold'])
				os.remove(save_location)
				d.query(f"""
					INSERT INTO DOWNLOAD_LOG(SAVED_USER,POSTED_BY,DATE_DOWNLOADED,URL,TITLE,SUB_REDDIT,
								PERMALINK,IS_ALBUM,ALBUM_INDEX,ALBUM_URL,FILE_NAME,POSTED_DATE
								,UP_VOTES,DOWNLOAD_FAILED,ERROR_MSG) 
					VALUES('{cfg.username}','{user}','{t.nowDateTime()}','{url}','{d.sqlQuotes(title)}',
							'{subr}','{perm}',{d.nullValue(alb)},{d.nullValue(alb_i,is_int=True)},
							{d.nullValue(alb_url)},'{file_name}','{post_time}',{up_votes},1,'{error_msg}');
					""")
			else:
				download_count += 1
				d.query(f"""
					INSERT INTO DOWNLOAD_LOG(SAVED_USER,POSTED_BY,DATE_DOWNLOADED,URL,TITLE,SUB_REDDIT,
								PERMALINK,IS_ALBUM,ALBUM_INDEX,ALBUM_URL,FILE_NAME,POSTED_DATE,UP_VOTES) 
					VALUES('{cfg.username}','{user}','{t.nowDateTime()}','{url}','{d.sqlQuotes(title)}',
							'{subr}','{perm}',{d.nullValue(alb)},{d.nullValue(alb_i,is_int=True)},
							{d.nullValue(alb_url)},'{file_name}','{post_time}',{up_votes});
					""")
		time.sleep(2)
	except Exception as e:
		cprint(f'Unable to download: ^^^{url}^^^ The error was: {str(e)}','red', 'on_cyan',attrs=['bold'])
		d.query(f"""
			INSERT INTO DOWNLOAD_LOG(SAVED_USER,POSTED_BY,DATE_DOWNLOADED,URL,TITLE,SUB_REDDIT,
						PERMALINK,IS_ALBUM,ALBUM_INDEX,ALBUM_URL,FILE_NAME,POSTED_DATE
						,UP_VOTES,DOWNLOAD_FAILED,ERROR_MSG) 
			VALUES('{cfg.username}','{user}','{t.nowDateTime()}','{url}','{d.sqlQuotes(title)}',
					'{subr}','{perm}',{d.nullValue(alb)},{d.nullValue(alb_i,is_int=True)},
					{d.nullValue(alb_url)},'{file_name}','{post_time}',{up_votes},1,'{str(e)}');
			""")

d.query(f"""UPDATE 	JOB_TRACKER 
			SET 	END_DATE = '{t.nowDateTime()}',
					DOWNLOAD_COUNT = {download_count} 
			WHERE 	ID = {job_id};""")

time_took = round(time.time() - start_time,3)

print(f'\nProcess completed in {t.humanTime(time_took)}...')

print('\nProcess Complete!\n')