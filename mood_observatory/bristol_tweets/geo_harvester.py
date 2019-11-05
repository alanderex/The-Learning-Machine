import tweepy
import json
import sys
import signal
import subprocess
import os
from pymongo import MongoClient

import mongo_ops
import credentials
import geo_boxes
import env_config

def signal_handler(sig, frame):
    print(f"\n\nCtrl-c, ok got it, just a second while I try to exit gracefully...")
    mongo_ops.stop_mongo()
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

        # export the most recent tweet as csv so it can be sentiment analysed
        mongo_ops.export_latest_tweet(mongoexport_executable_path)


if __name__ == "__main__":

    ## Set up interrupt signal handling and environment paths
    signal.signal(signal.SIGINT, signal_handler)
    env = env_config.EnvironmentConfig()

    ## check if MongoDB is present and correct
    try:
        mongod_executable_path = subprocess.check_output(['which', 'mongod']).decode('utf-8').strip()
    except:
        print(f"You don't seem to have MongoDB installed. Stopping.")
        sys.exit()
    try:
        mongoexport_executable_path = subprocess.check_output(['which', 'mongoexport']).decode('utf-8').strip()
    except:
        print(f"Mongoexport seems missing... stopping.")
        sys.exit()
    try:
        mongodump_executable_path = subprocess.check_output(['which', 'mongodump']).decode('utf-8').strip()
    except:
        print(f"Mongodump seems missing... stopping.")
        sys.exit()

    ## Check or make directory structure
    if not os.path.exists(env.run_folder + '/db'):
        print(f"MongoDB database folder seems absent, creating folder...")
        os.makedirs(env.run_folder + '/db')
    if not os.path.exists(env.run_folder + '/db_logs'):
        print(f"DB log folder seems absent, creating folder...")
        os.makedirs(env.run_folder + '/db_logs')

    mongo_ops.start_mongo(mongod_executable_path, env.db_path, env.db_log_filename)
    auth = tweepy.OAuthHandler(credentials.CONSUMER_KEY, credentials.CONSUMER_SECRET)
    auth.set_access_token(credentials.ACCESS_TOKEN, credentials.ACCESS_TOKEN_SECRET)
    stream_listener = StreamListener(api=tweepy.API(wait_on_rate_limit=True))
    stream = tweepy.Stream(auth=auth, listener=stream_listener)
    stream.filter(locations=geo_boxes.boxes)
