from flask import Flask, render_template, request, session, g, redirect, url_for,abort
from flask import send_file

import jinja2
import json
import urllib
import httplib2
import sqlite3
import os


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


app = Flask(__name__)

@app.route("/")
def index():
	template = JINJA_ENVIRONMENT.get_template('templates/index.html')
	return template.render()

if __name__ == "__main__":
    app.run()