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
from src.Backend.VideoDB import VideoSelect
from src.Backend.VideoWriter import VideoWriter

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

app = Flask(__name__)
app.debug = True

# MARK - Database functions and info
database = Database()
select = VideoSelect()
writer = VideoWriter()

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



#if __name__ == "__main__":
#    app.run()

mediaFile = 'media/debate.mp4'
dataFile = 'data.json'

import json
from vaderSentiment.vaderSentiment import sentiment as vaderSentiment

def wordIn(comment, corpus):
    return any([comment.find(c) != -1 for c in corpus])

keywordsForTrump = ['he', 'Trump', 'Donald']
keywordsForClinton = ['she', 'Clinton', 'Hillary']

def getSentiment(comment):
    sent = vaderSentiment(comment.encode('utf-8'))
    pos = sent['pos']
    neg = sent['neg']
    return pos >= neg

corpus = keywordsForClinton
desiredSent = False
filter_comments = True

def filterFun(c):
    return getSentiment(c)==desiredSent and wordIn(c, corpus)


with open(dataFile,'r') as f:
    fileStr = f.read()
    jsonStr = json.loads(fileStr)
    intervalSize = int(jsonStr["intervalSize"])
    commentStr = jsonStr["comments"]

    sorted_comment_keys = sorted(commentStr.keys(), key = lambda k: int(k))
    print(sorted_comment_keys)

    x = [int(s) for s in sorted_comment_keys]
    commentData = None
    if (filter_comments):
	commentData = [[c for c in commentStr[k]['comment_data'] if filterFun(c)] for k in sorted_comment_keys]
    else:
	commentData = [[c for c in commentStr[k]['comment_data']] for k in sorted_comment_keys]
    
    y = [len(commentData[i]) for i in xrange(len(commentData))]
    print(sum(y))
   
    smoothed = select.smoothFeature(select.normalizeFeature(y), 1)
    print(smoothed)

    topIntervals = select.processFeature(x, y, 6*intervalSize, 5, 1)
    print([interval for interval in topIntervals])

    ranges = [interval[:2] for interval in topIntervals]
    
    comments = []
    for ind in xrange(len(ranges)):
	r = ranges[ind]

        start_key = (r[0] / intervalSize)
	end_key = ((r[1] + intervalSize - 1) /intervalSize)
	
	interval_comments = []
	
	for t in xrange(start_key, end_key+1):
	    coms = commentData[t] 
	    interval_comments.extend(coms)
	print(len(interval_comments))

	#comments.append(interval_comments)
	with open('media/temp/comments-%d.txt'%(ind), 'w') as outf:
	    json.dump(interval_comments, outf)

    writer.get_video_clips(mediaFile, 'media/temp', ranges, 0) 

