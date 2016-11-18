import os
import sys

import requests
import urllib2
import json	

import datetime
from dateutil import parser
from collections import Counter

import matplotlib.pyplot as plt

def request_video(videoid, access_token):

	endpoint = 'https://graph.facebook.com/v2.8'
	#access_token='EAACEdEose0cBAHFPMoobVMkxxWagM9i1SrJY1JKEdLd0xOaT5GqCOLnrFcT4ZA0v0Lr9wxrJKwRCHZBiZApuE7pVjpbIQR6lFJkJCVJ8WdMkfdmr1kPbKgf1GnT0oOvAgMbjP5DGy3Q06W8vSOt87CC8gZCgOLGiqZCoZApxkitQZDZD'
	fb_graph_url = endpoint+ '/' + videoid + '?fields=comments,length,scheduled_publish_time,created_time,backdated_time&limit=1000&access_token='+access_token

	
	resp = requests.get(fb_graph_url)

	data = json.dumps(resp.json(), sort_keys=True, indent=4, separators=(',',': '))
	print data
	d = json.loads(data)
	print d.keys()
	print d['created_time']
	duration = d['length']
	resp=requests.get(d['comments']['paging']['next'])
	print resp.json()
	data = json.dumps(resp.json(), sort_keys=True, indent=4, separators=(',',': '))
	d = json.loads(data)

	comment_data = []

	while('next' in d['paging']):

		resp=requests.get(d['paging']['next'].replace('&limit=25','&limit=500'))
		data = json.dumps(resp.json(), sort_keys=True, indent=4, separators=(',',': '))

		for comment in resp.json()['data']:
			# print comment
			comment_data.append((parser.parse(comment['created_time'], ignoretz=True), comment['message']))
		d = json.loads(data)

	# with open("result.json", 'w') as f:
	# 	f.write(comment_data)


	comment_data = sorted(comment_data, key=lambda comment: comment[0])

	print comment_data
	initial_time = comment_data[0][0]
	end_time = comment_data[-1][0]
	counts = []

	features = {}
	features['comments'] = {}
	features['intervalSize'] = 30

	countZeros = 0

	maxC = 0 
	print int(duration)
	print initial_time
	final_time = initial_time + datetime.timedelta(0,int(duration))
	seconds = 0
	while (initial_time < final_time):

		next_time = initial_time + datetime.timedelta(0,30)
		print next_time
		print initial_time + datetime.timedelta(0,int(duration))
		count = len([x for x in comment_data if (x[0] > initial_time and x[0] < next_time)])
		if not count:
			counts.append(count)
			countZeros = 0
		else:
			countZeros += 1
		if count > maxC:
			maxC = count


		features['comments'][str(seconds * 30)] = count
		seconds += 1
		#print next_time
		initial_time = next_time


	with open('data.json', 'w') as outfile:
		json.dump(features, outfile)
	k = 10

	#print json.dumps(resp.json(), sort_keys=True, indent=4, separators=(',',': '))

def main(args):

	request_video(args[1], args[2])

	return


if __name__=='__main__':
	sys.exit(main(sys.argv))