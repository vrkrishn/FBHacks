
import os
import sys

import requests
import urllib2
import json	


def request_video(id, access_token):

	endpoint = 'https://graph.facebook.com/v2.8'
	#access_token='EAACEdEose0cBAHFPMoobVMkxxWagM9i1SrJY1JKEdLd0xOaT5GqCOLnrFcT4ZA0v0Lr9wxrJKwRCHZBiZApuE7pVjpbIQR6lFJkJCVJ8WdMkfdmr1kPbKgf1GnT0oOvAgMbjP5DGy3Q06W8vSOt87CC8gZCgOLGiqZCoZApxkitQZDZD'
	fb_graph_url = endpoint+ '/' + 'ShaileneWoodley' + '/videos?fields=live_status,source&access_token='+access_token



	resp = requests.get(fb_graph_url)

	print json.dumps(resp.json(), sort_keys=True, indent=4, separators=(',',': '))

def main(args):

	request_video(args[1], args[2])

	return


if __name__=='__main__':
	sys.exit(main(sys.argv))
