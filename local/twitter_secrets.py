import tweepy


def twitter_api(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET):
    auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)
    return api


# Twitter Consumer API keys
myCK = ""
myCS = ""
myAT = ""
myAS = ""
BEARER_TOKEN = ""

my_twitter_api = twitter_api(myCK, myCS, myAT, myAS)
