import numpy as np
from scipy.ndimage import gaussian_filter1d

class VideoSelect(object):
	
	def smoothFeature(self, feature, sigma):
		return gaussian_filter1d(feature, sigma)
	
	def normalizeFeature(self, feature):
		scale = np.max(feature) - np.min(feature)
		return (feature - np.min(feature))/float(scale)
		
	def getLocalMaxima(self, feature, times):
		
		maxima = []
		for i in xrange(len(feature)):
			
			leftMaxima = (i == 0) or (feature[i] > feature[i-1])
			rightMaxima = (i == len(feature) - 1) or (feature[i] > feature[i+1])
			
			if (leftMaxima and rightMaxima):
				maxima.append((times[i], feature[i]))
				
		return maxima
		
		
	def getSmoothedIntervals(self, maxima, windowSize, sigma):
		
		if (len(maxima) == 0):
			return []
			
		nClusters = 1
		clusters = [0 for i in xrange(len(maxima))]
		for i in xrange(1,len(maxima)):
			
			last_time, last_value = maxima[i-1]
			time, value = maxima[i]
			
			if (abs(time - last_time) <= windowSize):
				clusters[i] = clusters[i-1]
			else:
				clusters[i] = clusters[i-1] + 1
				nClusters = nClusters + 1
				
		intervals = []
		# Get the start time for the first maxima
		currentCluster = 0
		startMaxima = maxima[0]
		endMaxima = maxima[0]
		maxValue = maxima[0][1]
		
		for i in xrange(1, len(clusters)):
			if (clusters[i] == currentCluster):
				#increment the interval time
				endMaxima = maxima[i]
				if (maxima[i][1] > maxValue):
					maxValue = maxima[i][1]
			else:
				# Create interval between maxima[startCluster] and maxima[i-1]
				# interval is (start time, endtime, max_value)
				intervals.append((startMaxima[0]-windowSize/2, endMaxima[0]+windowSize/2, maxValue))
				startMaxima = maxima[i]
				endMaxima = maxima[i]
				maxValue = maxima[i][1]
		
		intervals.append((startMaxima[0]-windowSize/2, endMaxima[0]+windowSize/2, maxValue))
		return intervals
		
		
	def sortIntervalsByValue(self, intervals):
		return sorted(intervals, key=lambda interval: -interval[2])
		
		
	def getTopKVideoClips(self, sortedIntervals, k):
		if (k > len(sortedIntervals)):
			return sortedIntervals
		else:
			return sortedIntervals[:k]
			
			
	def processFeature(self, times, feature, windowSize, k, sigma):
		smoothed = self.smoothFeature(feature, sigma)
		normalized = self.normalizeFeature(smoothed)
		maxima = self.getLocalMaxima(normalized, times)
		intervals = self.getSmoothedIntervals(maxima, windowSize,sigma)
		sortedIntervals = self.sortIntervalsByValue(intervals)
		topK = self.getTopKVideoClips(sortedIntervals, k)
		return topK
		
		

if __name__ == '__main__':
	
	import matplotlib.pyplot as plt
	
	V = VideoSelect()
	n = 100
	data = np.random.rand(n)
	#data[10] = 20
	#data[15] = 30
	times = np.array(range(n))
	
	k = 3
	sigma = 2
	
	windows = [3, 5,10]
	
	plt.subplot(len(windows)+3,1,1)
	plt.plot(times, data)
	
	smoothed = V.smoothFeature(data, sigma)
	plt.subplot(len(windows)+3,1,2)
	plt.plot(times, smoothed)
	
	
	normalized = V.normalizeFeature(smoothed)
	maxima = V.getLocalMaxima(normalized, times)
	plt.subplot(len(windows)+3,1,3)
	plt.plot([m[0] for m in maxima], [m[1] for m in maxima])
	
	for i in xrange(len(windows)):
		
		w = windows[i]
		topInterval = V.processFeature(times, data, w, k, sigma)
		
		plt.subplot(len(windows)+3,1,4+i)
		
		print(len(topInterval))
		for interval in topInterval:
			plt.plot([interval[0], interval[1]], [interval[2], interval[2]])
			
		plt.axis([min(times), max(times), 0, 2])
			
	plt.show()
