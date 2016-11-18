from pyqt_fit import kde
import numpy as np
import unicodedata

class TweetAnalytics(object):

    def get_kde(self, query_result, bandwidth, min_time, max_time):

        data = query_result['tweet_created'].values()
        est = kde.KDE1D(data, bandwidth=bandwidth)
        return est

    def get_local_maxima_kde(self, est, min_time, max_time):

        x = np.linspace(min_time, max_time, num=(max_time-min_time))
        y = est(x)
        maxima = []
        for i in xrange(1,len(x)-1):

            i_x = x[i]
            if (y[i-1] < y[i] and y[i+1] < y[i]):
                maxima.append((i_x, y[i]))

        return maxima


    def tweets_by_range(self, query_result, ranges, added_off):

        tweets = []
        for a, b in ranges:
            r_i = a - added_off
            r_j = b - added_off

            tweet = []
            for k in query_result['tweet_created'].keys():
                t = query_result['tweet_created'][k]
                if (r_i <= t and t <= r_j):
                    text = query_result['text'][k]
                    tweet.append(unicodedata.normalize('NFKD', text).encode('ascii','ignore'))
            tweets.append(tweet)

        return tweets


    def maxima_to_ranges(self, maxima, min_time, max_time, window_size, vid_buffer, y_thresh = 0, x_offset = 0):

        filtered_maxima = filter(lambda f: f[1] >= y_thresh, maxima)
        print filtered_maxima
        clusters = [0 for i in xrange(len(filtered_maxima))]

        if (len(filtered_maxima) == 0):
            return []

        # Get the clustering according to window
        clusters[0] = 1
        for i in xrange(1,len(filtered_maxima)):

            last_time, last_value = filtered_maxima[i-1]
            time, value = filtered_maxima[i]

            if (abs(time - last_time) <= window_size):
                clusters[i] = clusters[i-1]
            else:
                clusters[i] = clusters[i-1] + 1

        cluster_counts = [0 for i in xrange(max(clusters))]
        for i in xrange(1,max(clusters)+1):
            d = filter(lambda c: c == i, clusters)
            cluster_counts[i-1] = len(d)


        #Get the ranges
        ranges = []
        c_i = 0
        for i in xrange(len(cluster_counts)):

           ms_time, ms_value = filtered_maxima[c_i]
           me_time, me_value = filtered_maxima[c_i + cluster_counts[i]-1]
           c_i = cluster_counts[i] + c_i


           v_min = max(ms_time - vid_buffer + x_offset, min_time)
           v_max = min(me_time + vid_buffer + x_offset, max_time)

           ranges.append((v_min, v_max))

        return ranges











