from flask import Flask, render_template, request, session, g, redirect, url_for,abort
from flask import send_file
from flask import g

import jinja2
import json
import urllib
import httplib2
import sqlite3
import os

from src.Service.Database import Database

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

app = Flask(__name__)
app.debug = True

# MARK - Database functions and info
database = Database()

@app.route("/")
def index():
	template = JINJA_ENVIRONMENT.get_template('templates/index.html')
	return template.render()

@app.route("/videos")
def videos():
	template = JINJA_ENVIRONMENT.get_template('templates/index.html')
	return template.render(rows = database.getRows())

@app.route("/getPlaces", methods=["POST"])
def getLocations():
	template = JINJA_ENVIRONMENT.get_template('templates/index.html')
	result = database.getPlaces()
	return json.dumps(result)

@app.route("/getSubjects", methods=["POST"])
def getSubjects():
	template = JINJA_ENVIRONMENT.get_template('templates/index.html')
	result = database.getSubjects()
	return json.dumps(result)

# Returns a dictionary of videos sorted by subject
@app.route("/getVideosByLocation/<place>", methods=["POST"])
def getVideosByLocation(place):
	return json.dumps(database.getVideosForPlace(place))

@app.route("/getVideosBySubject/<subject>", methods=["POST"])
def getVideosBySubject(subject):
	return json.dumps(database.getVideosForSubject(subject))
	

@app.route("/resetdb")
def resetdb():
	template = JINJA_ENVIRONMENT.get_template('templates/index.html')
	database.resetDB()
	return template.render()



if __name__ == "__main__":
    app.run()
