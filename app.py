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


def getUniqueProperties(prop, table):
	with sqlite3.connect(DATABASE) as con:
		query = "SELECT DISTINCT %s from %s ;" %(prop, table)
		cur = con.cursor()
		cur.execute(query)
		rows = cur.fetchall()
		#print rows
		return [row[0] for row in rows]

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
			print("Starting to add video.")
			query = "INSERT INTO videos (id , length , place , source , title , content_category , universal_video_id , live_status , created_time , description , auto_generated_captions , captions , comments , likes , reactions , sponsor_tags , tags , video_insights) VALUES (? ,? , ? , ?,? ,? , ? , ?,? ,? , ? , ?,? ,? , ? , ?, ?, ?)"
			cur = con.cursor()
			cur.execute(query, (id , length , place , source , title , content_category , universal_video_id , live_status , created_time , description , auto_generated_captions , captions , comments , likes , reactions , sponsor_tags , tags , video_insights))
			print("Starting to add video.")
			con.commit()
			print("Starting to add video.")
			print("Video added.")
			return True
	except:
		con.rollback()
		return False

#addVideo(4 , 3 , "test" , "source" , "title" , "content_category" , 1 , "live_status" , "created_time" , "description" , "auto_generated_captions" , "captions" , "comments" , 1 , "reactions" , "sponsor_tags" , "tags" , "video_insights")
#addVideo(3 , 3 , "test" , "source" , "title" , "test" , 1 , "live_status" , "created_time" , "description" , "auto_generated_captions" , "captions" , "comments" , 1 , "reactions" , "sponsor_tags" , "tags" , "video_insights")



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
	template = JINJA_ENVIRONMENT.get_template('templates/index.html')
	with sqlite3.connect(DATABASE) as con:
		query = "SELECT * FROM videos;"
		cur = con.cursor()
		cur.execute(query)
		rows = cur.fetchall()
		return template.render(rows = rows)
		

@app.route("/getPlaces", methods=["POST"])
def getLocations():
	template = JINJA_ENVIRONMENT.get_template('templates/index.html')
	result = getUniqueProperties("place", "videos")
	return json.dumps(result)

@app.route("/getSubjects", methods=["POST"])
def getSubjects():
	template = JINJA_ENVIRONMENT.get_template('templates/index.html')
	result = getUniqueProperties("content_category", "videos")
	return json.dumps(result)

# Returns a dictionary of videos sorted by subject
@app.route("/getVideosByLocation/<place>", methods=["POST"])
def getVideosByLocation(place):
	result = {}
	with sqlite3.connect(DATABASE) as con:
		query = "SELECT * FROM videos WHERE place = '%s' ORDER BY content_category" %(place)
		cur = con.cursor()
		cur.execute(query)
		rows = cur.fetchall()
		for row in rows:
			content_category = row[5]
			if content_category not in result:
				result[content_category] = []
			result[content_category].append(row)
		return json.dumps(result)
	



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
