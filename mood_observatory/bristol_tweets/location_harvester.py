import tweepy
import json
from pymongo import MongoClient


class StreamListener(tweepy.StreamListener):

    """tweepy.StreamListener is a class provided by tweepy used to access
    the Twitter Streaming API to collect tweets in real-time.
    """

    def on_connect(self):

        """Lets you know the connection was successful"""

        print("You're connected to the streaming server.")

    def on_error(self, status_code):

        """Lets you know that something went wrong"""

        print("Error: " + repr(status_code))
        return False

    def on_data(self, data):

        """Each time a new tweet is streamed in, it is stored in MongoDB"""

        client = MongoClient()

        # Connect to or initiate a database called 'tweets'
        db = client.tweets

        # Deal with the incoming json
        datajson = json.loads(data)

        # Only store tweets in English;
        # put into 'tweet_collection' of the 'tweets' database.
        if "lang" in datajson and datajson["lang"] == "en":
            db.tweet_collection.insert_one(datajson)


if __name__ == "__main__":

    # These are provided to you through the Twitter API after you create a account
    consumer_key = ""
    consumer_secret = ""
    access_token = ""
    access_token_secret = ""

    auth1 = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth1.set_access_token(access_token, access_token_secret)

    # boxes are the longitude, latitude coordinate corners for geoboxes
    # The first two define the SW corner of the box and the second two define the NE corner of the box.
    # THESE ARE NOT INTUITIVE AS LAT/LONG ARE REVERSED FROM CONVENTION :/ :( weird
    # examples:
    # boxes = [-124.7771694, 24.520833, -66.947028, 49.384472,        # Contiguous US
    #             -164.639405, 58.806859, -144.152365, 71.76871,         # Alaska
    #             -160.161542, 18.776344, -154.641396, 22.878623,        # Hawaii
    #             -9.502491, 48.309957, 1.413503, 60.992262,             # UK + Ireland
    #             -16.869498, 26.618414, 52.220250, 70.257538]           # Europe

    boxes = [-2.695672, 51.392892, -2.446455, 51.562357]  # Bristol
    stream_listener = StreamListener(api=tweepy.API(wait_on_rate_limit=True))
    stream = tweepy.Stream(auth=auth1, listener=stream_listener)
    stream.filter(locations=boxes)
