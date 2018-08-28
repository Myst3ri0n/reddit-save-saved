import praw
import config as cfg
import re
import time
import urllib.request
from requests_html import HTMLSession

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
album_count = 1
for link in saved_posts:
	url   = link.url
	title = link.title
	if url[-3:].upper() in ['JPG','PNG','GIF']:
		titles.append(title)
		links.append(url)
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
			album_index+=1

		album_count+=1

print(f'{album_count} albums detected...\n')

print(f'{len(links)} images will be downloaded...\n')

#download files
index = 0
for l in links:
	url = l
	print(f'Downloading: {titles[index]}  ({url})')
	file_name = re.search(r'(?=\w+\.\w{3,4}$).+',url).group(0)
	try:
		urllib.request.urlretrieve(url,'saved/'+file_name)
	except:
		print(f'Unable to download: ^^^{url}^^^')
	time.sleep(2)
	index+=1

print('\nProcess Complete!')