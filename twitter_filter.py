import tweepy
import datetime
import json
import os
import nltk
from google_trans_new import google_translator
from tweet_storage_redis.tweet_store import TweetStore

nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

dir_name = os.path.dirname(__file__)
file_path = os.path.join(dir_name, 'config', 'api.json')

with open(file_path, encoding='utf-8') as f:
    twitter_api = json.loads(f.read())

consumer_key = twitter_api['consumer_key']
consumer_secret = twitter_api['consumer_secret']
access_token = twitter_api['access_token']
access_token_secret = twitter_api['access_token_secret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)
store = TweetStore()


class StreamListener(tweepy.Stream):

    def __init__(self, consumer_key, consumer_secret, access_token,access_token_secret):
        super().__init__(consumer_key, consumer_secret, access_token, access_token_secret)
        self.num_tweets = 0

    def on_status(self, status):
        if self.num_tweets < 15:
            if 'RT @' not in status.text:
                try:
                    translator = google_translator()
                    translated_text = translator.translate(text=status.text, lang_tgt='en')
                    analyzer = SentimentIntensityAnalyzer()
                    polarity = analyzer.polarity_scores(translated_text)['compound']

                    tweet_item = {
                        'id_str': status.id_str,
                        'text': status.text,
                        'polarity': polarity,
                        'username': status.user.screen_name,
                        'name': status.user.name,
                        'profile_image_url': status.user.profile_image_url,
                        'received_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }

                    store.push(tweet_item)
                    self.num_tweets += 1
                    print('Pushed to redis: ', tweet_item)
                except AttributeError:
                    pass
            else:
                return False

    def on_error(self, status_code):
        if status_code == 420:  # rate limited
            return False


# stream_listener = StreamListener(consumer_key, consumer_secret, access_token, access_token_secret)
# stream = tweepy.Stream(auth=api.auth, listener=stream_listener)

stream = StreamListener(consumer_key, consumer_secret, access_token, access_token_secret)
stream.filter(track=["@petermckinnon", "photography", "logo", "minimalistic", "wedding sweets", "vintage", "oldschool",
                     "industrial"]
              , languages=['en'])
