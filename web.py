import os
import random
from gcore import db
import sqlite3
from flask import Flask, request, render_template, redirect, url_for, flash, make_response, session, Markup, jsonify

app = Flask(__name__)



@app.route('/',methods=['GET','POST'])
def index():
	conn = sqlite3.connect('saved.db')
	conn.text_factory = str
	cur = conn.cursor()
	cur.execute('SELECT ID AS COUNT FROM DOWNLOAD_LOG')
	image_ids = cur.fetchall()
	if len(image_ids)<25:
		random_num = len(image_ids)
	else:
		random_num = 25
	img_ids = random.sample(range(len(list(image_ids))), random_num)
	cur.execute(f"""
			SELECT 	'static/saved/'||SUB_REDDIT||'/'||FILE_NAME AS FILE_NAME,
					TITLE AS TITLE,
					ID AS ID
			FROM 	DOWNLOAD_LOG
			WHERE 	ID IN ({', '.join(str(x) for x in img_ids)});
		""")
	fp_imgs = cur.fetchall()
	return render_template('index.html',images=fp_imgs)

@app.route('/search',methods=['GET', 'POST'])
def search():
	if request.method == 'POST':
		conn = sqlite3.connect('saved.db')
		conn.text_factory = str
		cur = conn.cursor()
		search_term = request.form['search']
		print(search_term)
		cur.execute(f"""
				SELECT 	'static/saved/'||SUB_REDDIT||'/'||FILE_NAME AS FILE_NAME,
						TITLE AS TITLE,
						ID AS ID
				FROM 	DOWNLOAD_LOG
				WHERE 	TITLE LIKE '%{search_term}%';
			""")
		search_images = cur.fetchall()
		return render_template('index.html',images=search_images)
	return render_template('index.html')


@app.route('/filter/gifs',methods=['GET','POST'])
def gifsOnly():
	conn = sqlite3.connect('saved.db')
	conn.text_factory = str
	cur = conn.cursor()
	cur.execute("SELECT ID AS COUNT FROM DOWNLOAD_LOG WHERE lower(FILE_NAME) LIKE '%gif%';")
	image_ids = cur.fetchall()
	if len(image_ids)<25:
		random_num = len(image_ids)
	else:
		random_num = 25
	img_ids = random.sample(range(len(list(image_ids))), random_num)
	cur.execute(f"""
			SELECT 	'static/saved/'||SUB_REDDIT||'/'||FILE_NAME AS FILE_NAME,
					TITLE AS TITLE,
					ID AS ID
			FROM 	DOWNLOAD_LOG
			WHERE 	ID IN ({', '.join(str(x) for x in img_ids)});
		""")
	fp_imgs = cur.fetchall()
	
	return render_template('subreddit.html',images=fp_imgs)


@app.route('/filter/images',methods=['GET','POST'])
def imagesOnly():
	conn = sqlite3.connect('saved.db')
	conn.text_factory = str
	cur = conn.cursor()
	cur.execute("""
				SELECT 	ID AS COUNT 
				FROM 	DOWNLOAD_LOG 
				WHERE 	lower(FILE_NAME) LIKE '%jpg%' 
						OR lower(FILE_NAME) LIKE '%png%';""")
	image_ids = cur.fetchall()
	if len(image_ids)<25:
		random_num = len(image_ids)
	else:
		random_num = 25
	img_ids = random.sample(range(len(list(image_ids))), random_num)
	cur.execute(f"""
			SELECT 	'static/saved/'||SUB_REDDIT||'/'||FILE_NAME AS FILE_NAME,
					TITLE AS TITLE,
					ID AS ID
			FROM 	DOWNLOAD_LOG
			WHERE 	ID IN ({', '.join(str(x) for x in img_ids)});
		""")
	fp_imgs = cur.fetchall()
	
	return render_template('subreddit.html',images=fp_imgs)

@app.route('/r/<subreddit>',methods=['GET','POST'])
def subredditPage(subreddit):
	conn = sqlite3.connect('saved.db')
	conn.text_factory = str
	cur = conn.cursor()
	print(subreddit)
	cur.execute(f"""
			SELECT 	'static/saved/'||SUB_REDDIT||'/'||FILE_NAME AS FILE_NAME,
					TITLE AS TITLE,
					ID AS ID
			FROM 	DOWNLOAD_LOG
			WHERE 	SUB_REDDIT='{subreddit}';
		""")
	imgs = cur.fetchall()
	
	return render_template('subreddit.html',images=imgs)

@app.route('/about')
def about():
	
	return render_template('about.html')

#json endpoints
@app.route('/json/subreddits')
def jsonSubs():
	conn = sqlite3.connect('saved.db')
	conn.text_factory = str
	cur = conn.cursor()
	cur.execute('SELECT DISTINCT SUB_REDDIT FROM DOWNLOAD_LOG ORDER BY SUB_REDDIT;')
	result=cur.fetchall()
	return jsonify(response=result)

@app.route('/json/image/<id>')
def jsonImage(id):
	conn = sqlite3.connect('saved.db')
	conn.text_factory = str
	cur = conn.cursor()
	cur.execute(f"""
		SELECT 	TITLE,
				SUB_REDDIT,
				URL,
				FILE_NAME,
				PERMALINK,
				POSTED_BY
		FROM 	DOWNLOAD_LOG
		WHERE 	ID={id}
		ORDER BY 
				SUB_REDDIT;
		
		""")
	result=cur.fetchall()
	return jsonify(response=result)


@app.errorhandler(404)
def page_not_found(e):
   return render_template('404.html'), 404


if __name__ == '__main__':
	host = os.getenv('IP','127.0.0.1')
	port  = int(os.getenv('PORT',5005))
	#app.debug = True
	#TEMPLATES_AUTO_RELOAD = True
	app.secret_key = 'klnadsfq3849t98q34jt89j'
	app.run(host=host, port=port, debug=True)