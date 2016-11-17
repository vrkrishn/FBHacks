# Module responsible for getting a tweet's candidate, subject, and sentiment
from TweetSelect import TweetSelect, Condition
import unicodedata
import re
import nltk


import pickle

class TrainUtil(object):

    @staticmethod
    def replaceTwoOrMore(s):
        #look for 2 or more repetitions of character and replace with the character itself
        pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
        return pattern.sub(r"\1\1", s)

    @staticmethod
    def getStopWordList(stopWordListFileName):
        #read the stopwords file and build a list
        stopWords = []
        stopWords.append('AT_USER')
        stopWords.append('URL')

        fp = open(stopWordListFileName, 'r')
        line = fp.readline()
        while line:
            word = line.strip()
            stopWords.append(word)
            line = fp.readline()
        fp.close()
        return stopWords

    @staticmethod
    def save_model(model, file):
        with open(file, 'wb') as f:
            pickle.dump(model, f)

    @staticmethod
    def load_model(file):
        model = None
        with open(file, 'rb') as f:
            model = pickle.load(f)

        return model


    @staticmethod
    def getFeatureVector(tweet, stopWords):
        featureVector = []
        #split tweet into words
        words = tweet.split()
        for w in words:
            #replace two or more with two occurrences
            w = TrainUtil.replaceTwoOrMore(w)
            #strip punctuation
            w = w.strip('\'"?,.')
            #check if the word stats with an alphabet
            val = re.search(r"^[a-zA-Z][a-zA-Z0-9]*$", w)
            #ignore if it is a stop word
            if(w in stopWords or val is None):
                continue
            else:
                featureVector.append(w.lower())
        return featureVector


class TweetClassifier(object):
    pass



# Classifier to determine a tweets classifier
class SentimentClassifier(object):

    def extract_feature(self, tweet):
        return {'contains(%s)'%word:word in tweet for word in self.dictionary}

    def train(self, database):

        self.stopwords = TrainUtil.getStopWordList('../media/stopwords.txt')


        TW = TweetSelect(database)
        query_result = TW.select(Condition())
        sentiments = query_result['sentiment']

        sentiment_names = set([str(v) for v in sentiments.values()])
        sentiment_names.discard('')

        training_dict = set()

        # Get dictionary
        for text in query_result['text'].values():
            tweet_str = unicodedata.normalize('NFKD', text).encode('ascii','ignore')
            tweet = TrainUtil.getFeatureVector(tweet_str, self.stopwords)
            for word in tweet:
                training_dict.add(word)

        self.dictionary = training_dict


        training_data = {}

        pos_samples= None

        for sentiment in sentiment_names:


            C = Condition()
            C.set_sentiment(sentiment)
            query_result = TW.select(C)
            print "Training Sentiment: ", sentiment, " Count: ", len(query_result['tweet_created'].keys())

            if (sentiment == 'Positive'):
                pos_samples = len(query_result['tweet_created'].keys())


            text_data = query_result['text']
            training_data[sentiment] = []
            i = 0
            for text in text_data.values():
                if (i > pos_samples):
                    break
                tweet_str = unicodedata.normalize('NFKD', text).encode('ascii','ignore')
                feature = TrainUtil.getFeatureVector(tweet_str, self.stopwords)
                training_data[sentiment].append(feature)
                i += 1

            training_data[sentiment] = [self.extract_feature(f) for f in training_data[sentiment]]


        classifier_data = []
        for sentiment in sentiment_names:
            for data in training_data[sentiment]:
                classifier_data.append((data, sentiment))

        print "Training Classifier"
        self.classifier = nltk.NaiveBayesClassifier.train(classifier_data)


    def evaluate(self, tweet_str):
        tweet = TrainUtil.getFeatureVector(tweet_str, self.stopwords)
        features = self.extract_feature(tweet)

        prediction = self.classifier.prob_classify(features)
        pred_prob = [(sample, prediction.prob(sample)) for sample in prediction.samples()]

        max_guess = max(pred_prob, key=lambda a:a[1])
        if (max_guess[1] > self.thresh):
            return max_guess[0], pred_prob
        else:
            return "Neutral", pred_prob


# Classifier to determine a tweets classifier
class CandidateClassifier(object):

    def extract_feature(self, tweet):
        return {'contains(%s)'%word:word in tweet for word in self.dictionary}

    def train(self, database):
        self.thresh = 0.65
        self.stopwords = TrainUtil.getStopWordList('../media/stopwords.txt')


        TW = TweetSelect(database)
        query_result = TW.select(Condition())
        candidates = query_result['candidate']

        candidate_names = set([str(v) for v in candidates.values()])
        candidate_names.discard('')

        training_dict = set()

        for candidate in candidate_names:

            for word in candidate.split(" "):
                training_dict.add(word.lower())

        training_dict = list(training_dict)
        self.dictionary = training_dict

        print training_dict

        self.classifiers = {}

        training_data = {}
        for candidate in candidate_names:

            print "Training Candidate: ", candidate
            C = Condition()
            C.set_candidate(candidate)
            query_result = TW.select(C)


            text_data = query_result['text']
            training_data[candidate] = []
            for text in text_data.values():
                tweet_str = unicodedata.normalize('NFKD', text).encode('ascii','ignore')
                feature = TrainUtil.getFeatureVector(tweet_str, self.stopwords)
                training_data[candidate].append(feature)

            training_data[candidate] = [self.extract_feature(f) for f in training_data[candidate]]


        classifier_data = []
        for candidate in candidate_names:
            for data in training_data[candidate]:
                classifier_data.append((data, candidate))

        self.classifier = nltk.NaiveBayesClassifier.train(classifier_data)

    def evaluate(self, tweet_str):
        tweet = TrainUtil.getFeatureVector(tweet_str, self.stopwords)
        features = self.extract_feature(tweet)

        prediction = self.classifier.prob_classify(features)
        pred_prob = [(sample, prediction.prob(sample)) for sample in prediction.samples()]
        return max(pred_prob, key=lambda a:a[1])[0], pred_prob


# Classifier to determine a tweets classifier
class SubjectClassifier(object):

    def extract_feature(self, tweet):
        return {'contains(%s)'%word:word in tweet for word in self.dictionary}

    def train(self, database):

        self.stopwords = TrainUtil.getStopWordList('../media/stopwords.txt')

        self.thresh = 0.65

        TW = TweetSelect(database)
        query_result = TW.select(Condition())
        subjects = query_result['subject_matter']

        subject_names = set([str(v) for v in subjects.values()])
        subject_names.discard('')
        subject_names.discard("Women's Issues (not abortion though)")

        training_dict = set()

        # Get dictionary
        for text in query_result['text'].values():
            tweet_str = unicodedata.normalize('NFKD', text).encode('ascii','ignore')
            tweet = TrainUtil.getFeatureVector(tweet_str, self.stopwords)
            for word in tweet:
                training_dict.add(word)

        self.dictionary = training_dict


        training_data = {}


        for subject in subject_names:


            C = Condition()
            C.set_subject(subject)
            query_result = TW.select(C)
            print "Training Subject: ", subject, " Count: ", len(query_result['tweet_created'].keys())

            text_data = query_result['text']
            training_data[subject] = []

            i = 0
            for text in text_data.values():
                if (i > 400):
                    break
                tweet_str = unicodedata.normalize('NFKD', text).encode('ascii','ignore')
                feature = TrainUtil.getFeatureVector(tweet_str, self.stopwords)
                training_data[subject].append(feature)
                i = i + 1

            training_data[subject] = [self.extract_feature(f) for f in training_data[subject]]


        classifier_data = []
        for subject in subject_names:
            for data in training_data[subject]:
                classifier_data.append((data, subject))

        print "Training Classifier"
        self.classifier = nltk.NaiveBayesClassifier.train(classifier_data)


    def evaluate(self, tweet_str):
        tweet = TrainUtil.getFeatureVector(tweet_str, self.stopwords)
        features = self.extract_feature(tweet)

        prediction = self.classifier.prob_classify(features)
        pred_prob = [(sample, prediction.prob(sample)) for sample in prediction.samples()]

        max_guess = max(pred_prob, key=lambda a:a[1])
        if (max_guess[1] > self.thresh):
            return max_guess[0], pred_prob
        else:
            return "None of the Above", pred_prob


#stopwords = TrainUtil.getStopWordList('./media/stopwords.txt')

if __name__ == '__main__':

    C = SentimentClassifier()
    C.train('./database.sqlite')
    TrainUtil.save_model(C, '../models/sentiment.classifier')

    D = SubjectClassifier()
    D.train('./database.sqlite')
    D.thresh = 0.45
    TrainUtil.save_model(D, '../models/subject.classifier')

    E = CandidateClassifier()
    E.train('./database.sqlite')
    TrainUtil.save_model(E, '../models/candidate.classifier')
