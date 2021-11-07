import tweepy
import datetime
import json
import os

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


class StreamListener(tweepy.Stream):

    def on_status(self, status):

        if ('RT @' not in status.text):
            tweet_item = {
                'id_str': status.id_str,
                'text': status.text,
                'username': status.user.screen_name,
                'name': status.user.name,
                'profile_image_url': status.user.profile_image_url,
                'received_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            print(tweet_item)

    def on_error(self, status_code):
        if status_code == 420: #rate limited
            return False


#stream_listener = StreamListener(consumer_key, consumer_secret, access_token, access_token_secret)
#stream = tweepy.Stream(auth=api.auth, listener=stream_listener)

stream = StreamListener(consumer_key, consumer_secret, access_token, access_token_secret)
stream.filter(track=["@WarbyParker", "@Bonobos", "@Casper", "logo_design", "@pless_pl",
                     "tort_weselny"])
