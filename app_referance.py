from flask import Flask,render_template, request, session, g, redirect, url_for,abort
from flask_wtf import Form
from flask import send_file

from functools import wraps, update_wrapper
#from wtforms import StringField, SubmitField
#from wtforms.validators import Required

from codes.TweetAnalytics import TweetAnalytics
from codes.TweetSelect import TweetSelect, Condition

from codes.TweetClassifier import TrainUtil, SentimentClassifier, SubjectClassifier, CandidateClassifier
from codes.TweetVideoWriter import TweetVideoWriter
from codes.TweetVisualize import TweetVisualize
import time
import matplotlib.pyplot as plt

############# CODE #################

TA = TweetAnalytics()

print "Loading Classifier Modules"
#sentimentClassifier = TrainUtil.load_model('models/sentiment.classifier')
#sentimentClassifier.thresh = 0.5
#candidateClassifier = TrainUtil.load_model('models/candidate.classifier')
#subjectClassifier = TrainUtil.load_model('models/subject.classifier')
#sentimentClassifier.thresh = 0.33
print "Finished Loading Classifier Modules"

TV = TweetVisualize()
TVW = TweetVideoWriter()

###################################
app = Flask(__name__)
app.config['DEBUG'] = True


import os


@app.template_filter('autoversion')
def autoversion_filter(filename):
      # determining fullpath might be project specific
    fullpath = os.path.join('some_app/', filename[1:])
    try:
        timestamp = str(os.path.getmtime(fullpath))
    except OSError:
        return filename
    newfilename = "{0}?v={1}".format(filename, timestamp)
    return newfilename

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/text2vec")
def text2vec():
    return render_template("text2vec.html")

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/tweetselect")
def tweetselect():
    data = 1
    return render_template("tweetselect.html", data=1)

@app.route("/submit_index", methods=['POST', 'GET'])
def submit_index():

    TS = TweetSelect('./codes/database.sqlite')

    candidate = request.form['Candidate']
    sentiment = request.form['Sentiment']
    subject = request.form['Subject']
    print candidate, sentiment, subject
    C = Condition()
    if (candidate is not None and candidate != ''):
        C.set_candidate(candidate)
    if (sentiment is not None and sentiment != ''):
        C.set_sentiment(sentiment)
    if (subject is not None and subject != ''):
        print "SUBJECT: ", subject
        C.set_subject(subject)

    C.set_start_time('2015-08-06 19:00:00')
    C.set_end_time('2015-08-06 21:00:00')

    start_time = '2015-08-06 19:00:00'
    end_time = '2015-08-06 21:00:00'
    s_time = TS.timestamp_to_time(start_time, 0)
    e_time = TS.timestamp_to_time(end_time, 0)

    query = TS.select(C)

    est = TA.get_kde(query, 30, s_time, e_time)
    maxima = TA.get_local_maxima_kde(est, s_time, e_time)
    ranges = TA.maxima_to_ranges(maxima, s_time, e_time, 150, 45, .0002, -30)
    tweets_by_range = TA.tweets_by_range(query, ranges, -30)

    output_dir = './static/media/clips'
    TVW = TweetVideoWriter()
    names = TVW.get_video_clips('static/media/GOP_Debate.mp4', output_dir, ranges, s_time - 1032)
    data = zip(names, tweets_by_range)

    return render_template('index_submit.html', names = names, d = data, t=int(time.time()))



@app.route("/submit_text2vec", methods=['POST', 'GET'])
def submit_text2vec():

    def plot_bar(filename, bar_probs):

        f = plt.figure()
        bins = range(len(bar_probs))
        plt.bar(bins, [b[1] for b in bar_probs])
        plt.xticks(bins, [b[0] for b in bar_probs], rotation=45)
        plt.gcf().tight_layout()
        plt.gcf().subplots_adjust(bottom=0.15)

        plt.gcf().savefig(filename)
        return filename

    tweet = request.form['Tweet']

    sent_label, sent_probs = sentimentClassifier.evaluate(tweet)
    cand_label, cand_probs = candidateClassifier.evaluate(tweet)
    subj_label, subj_probs = subjectClassifier.evaluate(tweet)

    subj_graph = plot_bar('static/figures/subj_probs.png', subj_probs)
    sent_graph = plot_bar('static/figures/sent_probs.png', sent_probs)
    cand_graph = plot_bar('static/figures/cand_probs.png', cand_probs)

    return render_template('text2vec_submit.html', subj_I = subj_graph, sent_I = sent_graph, cand_I = cand_graph,
                                                   subject = sent_label, sentiment = sent_label, candidate = cand_label, t=int(time.time()))


@app.route("/submit_tweetselect", methods=['POST', 'GET'])
def submit_tweetselect():

    TS = TweetSelect('./codes/database.sqlite')

    candidate = request.form['Candidate']
    sentiment = request.form['Sentiment']
    subject = request.form['Subject']
    print candidate, sentiment, subject
    C = Condition()
    if (candidate is not None and candidate != ''):
        C.set_candidate(candidate)
    if (sentiment is not None and sentiment != ''):
        C.set_sentiment(sentiment)
    if (subject is not None and subject != ''):
        C.set_subject(subject)

    C.set_start_time('2015-08-06 19:00:00')
    C.set_end_time('2015-08-06 21:00:00')

    start_time = '2015-08-06 19:00:00'
    end_time = '2015-08-06 21:00:00'
    s_time = TS.timestamp_to_time(start_time, 0)
    e_time = TS.timestamp_to_time(end_time, 0)

    query_result = TS.select(C)
    f = plt.figure()
    bin_size = 60
    x_bins = range(s_time, e_time, bin_size)
    TV.visualize_frequency(query_result, x_bins, bin_size)
    fig1 = plt.gcf()
    plt.gcf().tight_layout()

    fig1.savefig('./static/figures/visualize.png')

    f = plt.figure()
    est = TA.get_kde(query_result, 60, s_time, e_time)
    TV.visualize_kde(est, s_time, e_time, 1)
    fig2 = plt.gcf()
    plt.gcf().tight_layout()
    fig2.savefig('./static/figures/kde.png')

    return render_template('tweetselect_submit.html', kernel_image_url='static/figures/kde.png', viz_image_url='static/figures/visualize.png', t=int(time.time()))


if __name__ == '__main__':
    app.run()
