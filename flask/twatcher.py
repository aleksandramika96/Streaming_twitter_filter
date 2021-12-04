from flask import Flask, render_template
from tweet_storage_redis.tweet_store import TweetStore

import time

app = Flask(__name__)
store = TweetStore()

#decorator which tells the application which url should call the associated function
#route decorator in Flask is used to bind url to a function; for example app.route('/contact') def contact () : ... , user visit http://localhost:5000/contact url, output contact() function will be rendered in browser

# some example
# @app.route('/hello/<name>')
# def hello_name(name):
#     return f'Hello {name}'

@app.route('/')
def index():
    tweets = store.tweets()
    return render_template('index.html', tweets=tweets)

if __name__ == '__main__':
    app.run(debug=True) #app.run(host, port, debug, option)