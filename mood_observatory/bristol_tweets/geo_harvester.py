import tweepy
import json
from pymongo import MongoClient

import credentials

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

        # Only store tweets in English;
        # put into 'geotweets_collection' of the 'geotweets' database.
        if "lang" in datajson and datajson["lang"] == "en":
            db.geotweets_collection.insert_one(datajson)


if __name__ == "__main__":

    # boxes are the longitude, latitude coordinate corners for a box that restricts the
    # The first two define the SW corner, the second two define the NE corner.
    # THESE ARE NOT INTUITIVE AS LAT/LONG ARE REVERSED FROM CONVENTION, weird :/ :(
    # examples:
    #boxes = [-2.695672, 51.392892, -2.446455, 51.562357]        # Bristol
    #boxes = [-124.7771694, 24.520833, -66.947028, 49.384472,        # Contiguous US
    #             -164.639405, 58.806859, -144.152365, 71.76871,         # Alaska
    #             -160.161542, 18.776344, -154.641396, 22.878623,        # Hawaii
    #             -9.502491, 48.309957, 1.413503, 60.992262,             # UK + Ireland
    #             -16.869498, 26.618414, 52.220250, 70.257538]           # Europe

    boxes = [-2.695672, 51.392892, -2.446455, 51.562357]        # Bristol

    auth = tweepy.OAuthHandler(credentials.CONSUMER_KEY, credentials.CONSUMER_SECRET)
    auth.set_access_token(credentials.ACCESS_TOKEN, credentials.ACCESS_TOKEN_SECRET)
    stream_listener = StreamListener(api=tweepy.API(wait_on_rate_limit=True))
    stream = tweepy.Stream(auth=auth, listener=stream_listener)
    stream.filter(locations=boxes)
