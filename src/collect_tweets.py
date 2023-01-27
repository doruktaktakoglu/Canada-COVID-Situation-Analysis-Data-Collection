import os, sys, json, argparse, pandas, oauth2, urllib, re
from datetime import date, timedelta
from dateutil.parser import parse
from pathlib import Path

parentdir = Path(__file__).parents[1]
sys.path.append(parentdir)
yesterday = date.today() - timedelta(days=1)
date_before_yesterday = yesterday - timedelta(days=2)

# CONSTANTS
API_BASE_URL = 'https://api.twitter.com/1.1/search/tweets.json'

# Default values
NUM_TWEETS = 10
START_DATE = date_before_yesterday.strftime('%Y-%m-%d')
END_DATE = yesterday.strftime('%Y-%m-%d')

# ASSUMPTION - these are the only relevant search terms
SEARCH_TERMS = [
    'covid',
    '#covid',
    'vaccination',
    '#vaccination',
    'vaccine',
    '#vaccine',
    'pfizer',
    '#pfizer',
    'pfizer-biontech',
    '#pfizer-biontech',
    'moderna',
    '#moderna',
    'astrazeneca',
    '#astrazeneca',
]

# get arguments from command line
def getArgs():
    parser = argparse.ArgumentParser(description='Collect tweets from Twitter API')
    parser.add_argument('-n', '--num', default=NUM_TWEETS, help='Number of tweets to collect')
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('-s', '--start', default=START_DATE, help='Start date')
    parser.add_argument('-e', '--end', default=END_DATE, help='End date')
    args = parser.parse_args()
    return args

# get api login info for Twitter API
def getTwitterCredentials():
    keyFile = os.path.join(parentdir, 'credentials', 'twitter_api.json')
    with open(keyFile, 'r') as f:
        credentials = json.load(f)
    return credentials

def oauth_req(url):
    CONSUMER_KEY = getTwitterCredentials()['consumer_key']
    CONSUMER_SECRET = getTwitterCredentials()['consumer_secret']
    consumer = oauth2.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
    client = oauth2.Client(consumer)
    _, content = client.request(url)
    return content

# collect tweets
def collectTweets(search_terms, numTweets, start_date, end_date):
    tweets = []
    if len(search_terms) == 0: return tweets
    start_date = parse(start_date + ' 00:00:00 +0000')
    remaining = numTweets
    params = {
        "q": f'(({") OR (".join(search_terms)})) -is:retweet -is:reply',
        "result_type": "recent",
        "count": min(100, max(remaining, 10)),
        "until": end_date,
        "lang": "en",
        "geocode": "56.1304,-106.3468,1000km",
        "tweet_mode": "extended"
    }
    url = API_BASE_URL + '?' + urllib.parse.urlencode(params)
    tweets_set = set()
    while remaining > 0:
        try:
            response = oauth_req(url)
            data = json.loads(response)
            for tweet in data["statuses"]:
                # skip tweets outside of date range
                created_date = parse(tweet["created_at"])
                if created_date < start_date: continue
                # skip duplicate tweets
                text = clean_tweet(tweet["full_text"])
                if text in tweets_set: continue
                # parse tweet and add to results
                tweets.append({
                    "id": tweet["id_str"],
                    "author_id": tweet["user"]["id_str"],
                    "created_at": tweet["created_at"],
                    "retweet_count": tweet["retweet_count"],
                    "like_count": tweet["favorite_count"],
                    "location": tweet["user"]["location"],
                    "author_follower_count": tweet["user"]["followers_count"],
                    "text": text,
                })
                tweets_set.add(text)
                remaining -= 1
            # add pagination info to url
            meta_data = data["search_metadata"]
            if meta_data["next_results"] is None: break
            url = API_BASE_URL + meta_data["next_results"] + '&tweet_mode=extended'
        except Exception as e:
            print(f'Error: {e}')
            break
    return tweets[:numTweets]

# clean tweet
def clean_tweet(tweet):
    # remove urls from tweet
    tweet = re.sub(r'http\S+', '', tweet)
    # remove line breaks from tweet
    tweet = str(tweet).replace('\n', ' ')
    return tweet

# write tweets to tsv file
def writeTweetsToTsv(tweets, outFile):
    table = pandas.DataFrame(tweets)
    table.to_csv(outFile, sep='\t', index=False)

# main
def main():
    args = getArgs()
    tweets = collectTweets(SEARCH_TERMS, int(args.num), args.start, args.end)
    if args.output:
        writeTweetsToTsv(tweets, args.output)
    else:
        print(tweets)

if __name__ == '__main__':
    main()