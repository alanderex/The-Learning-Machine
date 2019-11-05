import tweepy
import json
import sys
import signal
from pymongo import MongoClient

import mongo_ops
import credentials
import geo_boxes

def signal_handler(sig, frame):
    print(f"\n\nCtrl-c, ok got it, just a second while I try to exit gracefully...")
    sys.exit(0)

class StreamListener(tweepy.StreamListener):

    """tweepy.StreamListener is a class provided by tweepy used to access
    the Twitter Streaming API to collect tweets in real-time.
    """

    def on_connect(self):

        """Lets you know the connection was successful"""

        print("Connected to the streaming server.")

    def on_error(self, status_code):

        """Lets you know that something went wrong"""

        print('Error: ' + repr(status_code))
        return False

    def on_data(self, data):

        """Each new streamed tweet is stored in MongoDB"""

        client = MongoClient()

        # Connect to or initiate a database called 'geotweets'
        db = client.geotweets

        # Deal with the incoming json
        datajson = json.loads(data)

        # put into 'geotweets_collection' of the 'geotweets' database.
        print("New tweet.")
        db.geotweets_collection.insert_one(datajson)


if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal_handler)
    mongo_ops.check_mongo()

    auth = tweepy.OAuthHandler(credentials.CONSUMER_KEY, credentials.CONSUMER_SECRET)
    auth.set_access_token(credentials.ACCESS_TOKEN, credentials.ACCESS_TOKEN_SECRET)
    stream_listener = StreamListener(api=tweepy.API(wait_on_rate_limit=True))
    stream = tweepy.Stream(auth=auth, listener=stream_listener)
    stream.filter(locations=geo_boxes.boxes)
