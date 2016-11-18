from flask import Flask, render_template, request, session, g, redirect, url_for,abort
from flask import send_file
from flask import g

import jinja2
import json
import urllib
import httplib2
import sqlite3
import os


# MARK - Database functions and info

DATABASE = "db/database.db"
conn = sqlite3.connect(DATABASE)
print("Opened Database Succesfully")
# def get_db():
	# db = getattr(g, "_database", None)
	# if db is None:
	# 	db = g._database = sqlite3.connect(DATABASE)
	# return db



#need to look at this later
# @app.teardown_appcontext
# def close_connection(exception):
# 	db = getattr(g, "_database", None)
# 	if db is not None:
# 		db.close


def getVideo(id):
	with sqlite3.connect(DATABASE) as con:
		query = "SELECT * FROM videos WHERE id = " + id + ";"
		cur = con.cursor()
		cur.execute(query)
		rows = cur.fetchall();
		return rows

def addVideo(id , length , place , source , title , content_category , universal_video_id , live_status , created_time , description , auto_generated_captions , captions , comments , likes , reactions , sponsor_tags , tags , video_insights):
	try:	
		with sqlite3.connect(DATABASE) as con:
			query = "INSERT INTO videos (id , length , place , source , title , content_category , universal_video_id , live_status , created_time , description , auto_generated_captions , captions , comments , likes , reactions , sponsor_tags , tags , video_insights) VALUES (? ,? , ? , ?,? ,? , ? , ?,? ,? , ? , ?,? ,? , ? , ?, ?, ?)"
			cur = con.cursor()
			cur.execute(query, (id , length , place , source , title , content_category , universal_video_id , live_status , created_time , description , auto_generated_captions , captions , comments , likes , reactions , sponsor_tags , tags , video_insights))
			cur.commit()
			print("Video added.")
			return True
	except: 
		con.rollback()
		return False

addVideo(1 , 2 , "place" , "source" , "title" , "content_category" , 1 , "live_status" , "created_time" , "description" , "auto_generated_captions" , "captions" , "comments" , 1 , "reactions" , "sponsor_tags" , "tags" , "video_insights")



JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)



app = Flask(__name__)
app.debug = True


@app.route("/")
def index():
	template = JINJA_ENVIRONMENT.get_template('templates/index.html')
	return template.render()



@app.route("/videos")
def videos():
	with sqlite3.connect(DATABASE) as con:
		query = "SELECT * FROM videos;"
		cur = con.cursor()
		cur.execute(query)
		rows = cur.fetchall()
		return template.render(rows = rows)
		




@app.route("/resetdb")
def resetdb():
	template = JINJA_ENVIRONMENT.get_template('templates/index.html')
	with sqlite3.connect(DATABASE) as con:
		drop = "DROP TABLE IF EXISTS videos;"
		create = "CREATE TABLE videos (id INTEGER, length TEXT, place TEXT, source TEXT, title TEXT, content_category TEXT, universal_video_id INTEGER, live_status TEXT, created_time TEXT, description TEXT, auto_generated_captions TEXT, captions TEXT, comments TEXT, likes INTEGER, reactions TEXT, sponsor_tags TEXT, tags TEXT, video_insights TEXT);"

		cur = con.cursor()
		cur.execute(drop)
		print("table videos droped")
		cur.execute(create)
		print("table videos created")
	return template.render()



if __name__ == "__main__":
    app.run()
