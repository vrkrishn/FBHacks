from FacebookVideo import FacebookVideo
import math

class VideoMetadata(FacebookVideo):
    
    # All videos are broken up into intervals of size x
    def getIntervalInSeconds(self):
        return 2
    
    def getVideoIntervals(self):
        return math.ceil(self.getLength() / self.getIntervalInSeconds())
    
    def getFrameLabels(self, frames):
        n = self.getVideoIntervals()
        assert(all([frameId < n for frameId in frames]))
        return [self.frameLabels[frameId] for frameId in frames]
        
    def getVideoLabels(self):
        return self.videoLabels
        
        
# VideoMetadata
#
# - For the entire video, we can have a set of generated tags
# - (i.e. actions, )
#