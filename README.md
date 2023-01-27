# data-collection
Code for collecting data from Twitter API

### Installation
1. Install required modules for project
```
pip install -r requirements.txt
```

2. Ensure you have `credentials/twitter_api.json` file. File should have format:
```
{
    "consumer_key": "<API KEY>",
    "consumer_secret": "<API KEY SECRET>",
}
```

### `src/collect_tweets.py`
Collects and saves tweets using the Twitter API.
Uses Twitter API v1.1 to search for tweets within Canada (geocode 56.1304,-106.3468,1000km).

`collect_tweets.py` accepts the following command-line arguments:
* -n : (Optional) The number of tweets to collect. Default is 10.
* -o : (Optional) The path to the output (TSV) file where the results should be saved. If no value is provided, output will be logged into stdout.
* -s : (OPTIONAL) The start date from which to collect tweets, i.e. tweets before this date will not be collected. By default it is the date before yesterday (e.g. 2021-11-13)
* -e : (OPTIONAL) The end date until which to collect tweets, i.e. tweets after this date will not be collected. By default it is the date of yesterday (e.g. 2021-11-14)

Example:
```
python3 ./src/collect_tweets.py -n 303 -o ./data/tweets.tsv
```

### Assumptions
1. For our analysis, only the following search terms are relevant when querying the Twitter API:
```
[
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
```

2. For our analysis, only the following fields are relevant from each tweet
```
[
    'id',
    'author_id',
    'created_at',
    'retweet_count',
    'like_count',
    'location',
    'author_follower_count',
    'text'
]
```

3. We chose to discard the tweets' author names to reduce bias when annotating data.


4. We only chose to collect original tweets (i.e. no replies or retweets) to make annotation easier.