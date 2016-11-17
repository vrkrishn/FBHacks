import matplotlib.pyplot as plt
import numpy as np

class TweetVisualize(object):
    
    def visualize_kde(self, est, min_time, max_time, scale_factor = 1.0):
        #kde = KernelDensity(kernel='gaussian', bandwidth = bandwidth)
        
        n_bins = (max_time - min_time) * 10
        x = np.linspace(min_time, max_time, num=n_bins)
        estimate = est(x)
        
        plt.plot(x, [e * scale_factor for e in estimate])
        
        num_ticks = 10
        x_ticks = [x[i] for i in xrange(0, len(x), len(x)/num_ticks)]
        x_tick_strs = [str(int(t/3600)) + ':' + str(int((t%3600)/60)) + ":" + str(int(t%60)) for t in x_ticks]
        
        plt.xticks(x_ticks, x_tick_strs, rotation=45, size='small')
        
        
    
    #Create a histogram of tweet counts based on the bins
    def visualize_frequency(self, query_result, x_bins, bin_size):
        
        def find_bin(t):
            
            for i in xrange(len(x_bins)):
                b = x_bins[i]
                if (t >= b and t < b + bin_size):
                    return i
            
            return -1
            
        y_bins = [0 for i in xrange(len(x_bins))]
        
        for key in query_result['tweet_created'].keys():
            time = query_result['tweet_created'][key]
            q_bin = find_bin(time)
            
            if (q_bin != -1):
                y_bins[q_bin] = y_bins[q_bin] + 1
        
        
        plt.bar(x_bins, y_bins, edgecolor = "none", color='r', width=bin_size)
        
        #show 10 ticks
        num_ticks = 10
        x_ticks = [x_bins[i] for i in xrange(0, len(x_bins), len(x_bins)/num_ticks)]
        x_tick_strs = [str(t/3600) + ':' + str((t%3600)/60) + ":" + str(t%60) for t in x_ticks]
        
        plt.xticks(x_ticks, x_tick_strs, rotation=45, size='small')
        
        