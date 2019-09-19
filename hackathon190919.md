# Activity Log

## Hackathon 19/09/2019

**Projects**: 
1 Learning Machine 
2 Emoji Mirror
3 Mood Observatory


### Goal for the End of the Day:

1. Emoji Mirror Demo on Laptop
2. Some geocoded tweets on a map - using mapbox (KS)


### Stuff we Need

1. Set of geotagged location Tweet (Al)
2. Frontend design for Learning Machine 
3. Database of faces to classify 
    - FER Kaggle ([link](./fer2013)) - [Dataset Page](https://www.kaggle.com/c/challenges-in-representation-learning-facial-expression-recognition-challenge/data)
4. Set of words to classify
    - use Dodds and Danforth, 2011 ([link](http://doi.org/10.1371/journal.pone.0026752))
5. M model for Learning Machine and database
6. GitHub Setup

### Comments on geotagged tweets

* tl;dr - geotagging with lat/long has been deprecated by Twitter in the last two months -.-
* There are three standard ways of acquiring: **twurl** in a shell, or **tweepy** or **twython** under python.
* The [Twitter docs](https://developer.twitter.com/en/docs/geo/places-near-location/api-reference/get-geo-search.html) talking about geolocations focuses on json objects which can become attributes of a tweet, rather than tweets themselves, so are a bit of a red herring.
* Docs referring to using twurl suggest that a search like this one should return geotagged tweets `twurl GET -H api.twitter.com "/1.1/search/tweets.json?q=geocode=52.25,-2.35,50km" | jq` , but this kind of search does not work any more. You get an empty json back.
* Twitter's [own example search queries](https://developer.twitter.com/en/docs/tweets/search/guides/standard-operators.html) are now out of date - searching for geocode using their example results in twitter thinking you are searching for the word "geocode" :/ :/ :/ !!!
* Tested - tweeting with geotagging active, then harvesting that tweet, results in a tweet with empty geotag fields.

* Alternatives:
  * Using historical geotagged tweets instead.
  * Making a list of well-visited and tweeted-about Bristol locations, assigning coordinates manually, then appending coords back onto tweets mentioning those locations.
  * Another activity, I thought an idea would be to pool Bristol or south-west tweets and have a history slider to see if patterns emerge in emotional content of those messages, on fine-grained hourly scales, or long-term say yearly scales.
  
