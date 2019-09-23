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
* Tested - tweeting with geotagging active, then harvesting that tweet, results in a tweet with empty geotag fields.
* There are three standard ways of acquiring: **twurl** in a shell, or **tweepy** or **twython** under python.
* The [Twitter docs](https://developer.twitter.com/en/docs/geo/places-near-location/api-reference/get-geo-search.html) talking about geolocations focuses on json objects which can become attributes of a tweet, rather than tweets themselves, so are a bit of a red herring.
* Docs referring to using twurl suggest that a search like this one should return geotagged tweets `twurl GET -H api.twitter.com "/1.1/search/tweets.json?q=geocode:52.25,-2.35,30km" | jq` , but the returned tweets have all geotag fields set to null.
* Twitter's [own example search queries](https://developer.twitter.com/en/docs/tweets/search/guides/standard-operators.html) have a typo in; there should be a ":" after "geocode", not "=" .
* This is weird though: if you go to a twitter geolocation website, they are still working. You can select a tweet that is recent and has geotags. Then harvest it, and it does indeed still have geotags. You can even indirectly get the same tweet by harvesting by location, and you get that tweet back. Very confusing. Perhaps they are phasing out and Bristol is already phased out? But why does geotag seach return results, without it knowing their location? For example, compare\
`twurl GET -H api.twitter.com "/1.1/search/tweets.json?q=geocode:51.27,-2.35,30km" | jq | grep -A2 coordinates`\
(tweets from 30km around Bristol, you get results, but coords are null)\
with this (random) person who geotags\
`twurl GET -H api.twitter.com "/1.1/search/tweets.json?q=from:JennyPimentel" | jq | grep -A2 coordinates`\
and the coordinate subfields are there... weird.

* Alternatives:
  * Using historical geotagged tweets instead.
  * Making a list of well-visited and tweeted-about Bristol locations, assigning coordinates manually, then appending coords back onto tweets mentioning those locations.
  * Another activity, I thought an idea would be to pool Bristol or south-west tweets and have a history slider to see if patterns emerge in emotional content of those messages, on fine-grained hourly scales, or long-term say yearly scales.

### Future meet goals (aside from get things done!)

* Valerio and Al will think about workflows to upskill everyone; we realise it's a priority to use this project to teach, involve, and increase confidence in plenty of areas :)

