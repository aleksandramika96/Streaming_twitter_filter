import tweepy
import datetime
import json
import os
import nltk
import google_trans_new
from google_trans_new import google_translator
import tweet_storage_redis
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

    def on_status(self, status):

        if ('RT @' not in status.text):
            translator = google_translator()
            translated_text = translator.translate(text=status.text, lang_tgt='en')
            analyzer = SentimentIntensityAnalyzer()
            polarity = analyzer.polarity_scores(translated_text)
            # compound = polarity['compound']

            tweet_item = {
                'id_str': status.id_str,
                'text': status.text,
                'polarity': polarity,
                # 'compound': compound,
                'username': status.user.screen_name,
                'name': status.user.name,
                'profile_image_url': status.user.profile_image_url,
                'received_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            store.push(tweet_item)
            print('Pushed to redis: ', tweet_item)

    def on_error(self, status_code):
        if status_code == 420:  # rate limited
            return False


# stream_listener = StreamListener(consumer_key, consumer_secret, access_token, access_token_secret)
# stream = tweepy.Stream(auth=api.auth, listener=stream_listener)

stream = StreamListener(consumer_key, consumer_secret, access_token, access_token_secret)
stream.filter(track=["@WarbyParker", "@Bonobos", "@Casper", "logo_design", "pizza", "wedding sweets"])
