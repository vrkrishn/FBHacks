import itertools
import sqlite3
import unicodedata

class Database(object):
	
	def __init__(self):
		self.dbroot = "db/database.db"
		self.conn = sqlite3.connect(self.dbroot)
		self.dbRootTable = 'videos'
		print("Opened Database Succesfully")
	
	def getSchema(self):
		return [
			"id", 
		"length", 
		"place", 
		"source", 
		"title", 
		"content_category",
		 "universal_video_id", 
		 "live_status", 
		 "created_time", 
		 "description", 
		 "auto_generated_captions", 
		 "captions", 
		 "comments", 
		 "likes", 
		 "reactions", 
		 "sponsor_tags", 
		 "tags", 
		 "video_likes"]
	
	def getVideoSchema(self):
		return ["place", "id", "source", "content_category", "likes"]
	
	# Get the rating of a video
	def getVideoRating(self, video):
		return video["likes"]
		
	# Get thee rating of a collection of videos
	def getVideoCollectionRating(self, videos):
		return max([self.getVideoRating(video) for video in videos])
		
	def convertRowToAscii(self,row):
		return unicodedata.normalize('NFKD', row).encode('ascii','ignore')
		
	def processRow(self, row):
		schema = self.getSchema()
		videoSchema = self.getVideoSchema()
		return {key : row[schema.index(key)] for key in videoSchema if key in schema }
		
	def getVideoRating(self, video):
		return video['likes']
		
	# Returns a set of videos based on a primary key
	def getVideos(self):
		query = "SELECT * FROM %s" %(self.dbRootTable)
		cur = conn.cursor()
		cur.execute(query)
		rows = cur.fetchall()
		return [self.processRow(row) for row in rows]
			
			
	def getVideosByPrimaryKey(self, key, value):
		
		with sqlite3.connect(self.dbroot) as conn:
			query = "SELECT * FROM %s WHERE %s = '%s'" %(self.dbRootTable, key, value)
			cur = conn.cursor()
			cur.execute(query)
			rows = cur.fetchall()
			
			return [self.processRow(row) for row in rows]
	
	def getDistinctForProperty(self, prop):
		with sqlite3.connect(self.dbroot) as con:
			query = "SELECT DISTINCT %s from %s ;" %(prop, self.dbRootTable)
			cur = con.cursor()
			cur.execute(query)
			rows = cur.fetchall()
			#print rows
			return [row[0] for row in rows]
	
	def resetDB(self):
		with sqlite3.connect(self.dbroot) as conn:
			drop = "DROP TABLE IF EXISTS %s;" %(dbRootTable)
			create = "CREATE TABLE %s (id INTEGER, length TEXT, place TEXT, source TEXT, title TEXT, content_category TEXT, universal_video_id INTEGER, live_status TEXT, created_time TEXT, description TEXT, auto_generated_captions TEXT, captions TEXT, comments TEXT, likes INTEGER, reactions TEXT, sponsor_tags TEXT, tags TEXT, video_insights TEXT);" %(self.dbRootTable)
			cur = conn.cursor()
			cur.execute(drop)
			cur.execute(create)
	
	################## Specific Queries ####################
	
	def getPlaces(self):
		return self.getDistinctForProperty("place")
		
	def getSubjects(self):
		return self.getDistinctForProperty("content_category")
		
	# The following Get function return
	#[
	#	{secondary: secondary value, videos : matching videos} 
	#] where all entries have a given primary key and are sorted
	# by the rating of the collection
	
	def getVideosForPlace(self, place):
		videos = self.getVideosByPrimaryKey("place", place)
		result = {}
		
		for video in videos:
			if (video['content_category'] not in result):
				result[video['content_category']] = []
			result[video['content_category']].append(video)
			
		data = [(k,v) for k,v in result.iteritems()]
		return [{'subject': a, 'videos': b} for a,b in sorted(data, key=lambda k: self.getVideoCollectionRating(k[1]))]
		
	def getVideosForSubject(self, subject):		
		videos = self.getVideosByPrimaryKey("content_category", subject)
		result = {}
		
		for video in videos:
			if (video['place'] not in result):
				result[video['place']] = []
			result[video['place']].append(video)
			
		data = [(k,v) for k,v in result.iteritems()]
		return [{'place': a, 'videos': b} for a,b in sorted(data, key=lambda k: self.getVideoCollectionRating(k[1]))]


if __name__ == '__main__':		
	
	D = Database()
	print D.getVideosForSubject("content_category")