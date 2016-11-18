import subprocess as sp
import os

class TweetVideoWriter(object):

    # Vid_start is passed in if the times the videos are taken at and the times generated
    # from Tweet analytics have a constant offset from each other
    def range_to_format(self, ranges, vid_start):

        times = []

        for i in xrange(len(ranges)):

            v_min, v_max = ranges[i]
            v_min = v_min - vid_start
            v_max = v_max - vid_start

            h_min = v_min / 3600
            m_min = v_min % 3600 / 60
            s_min = v_min % 60

            v_time = v_max - v_min

            h_time = v_time / 3600
            m_time = v_time % 3600 / 60
            s_time = v_time % 60

            min_str = "%02d:%02d:%02d" %(h_min, m_min, s_min)
            time_str = "%02d:%02d:%02d" %(h_time, m_time, s_time)

            times.append((min_str, time_str))

        return times


    def get_video_clips(self, video_file, output_dirname, s_ranges, vid_start):

        formats = self.range_to_format(s_ranges, vid_start)
        clip_names = [output_dirname + "/" + "clip_" + str(i) + ".mp4" for i in xrange(len(formats))]

        for i in xrange(len(formats)):
            print "Clipping Video %d" %i
            self.clip_video(clip_names[i], video_file, formats[i][0], formats[i][1])

        return clip_names



    def clip_video(self, output_file_name, video_file, cut_start, cut_time):
        print cut_start, cut_time
        ffmpeg_bin = "ffmpeg"
        pipe = sp.Popen([ffmpeg_bin, "-v", "quiet", "-y", "-i", video_file, "-vcodec", "copy", "-acodec", "copy", "-ss", cut_start, "-t", cut_time, "-sn", output_file_name])
        pipe.wait()
        return True

