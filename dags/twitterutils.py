"""
Twitter related utilities.
"""

import os
import datetime
import traceback
import json
import time
import pandas as pd
from twitter import *

def twitter_init(cf_t):
    """Function to set initial
    Args: A configuration dictionary.

    Returns: A configuration dictionary.
    """
    cf_t['path'] = os.getcwd()
    cf_t['names_path'] = cf_t['path'] + cf_t['config'] + "/" + cf_t['file']
    cf_t['data_path'] = cf_t['path'] + cf_t['data']
    return cf_t

def read_screen_names_df(cf_t):
    """Function to return screen names from a file.
    Args: A configuration file.

    Returns: A python dataframe.
    """
    df = pd.DataFrame.from_csv(cf_t['names_path'])
    df = df.drop_duplicates(subset='screen_name', keep="first")
    return df

def read_screen_names(cf_t):
    """Function to return screen names from a file.
    Args: A configuration file.

    Returns: A python list of twitter handles.
    """
    names = set()
    f = open(cf_t['names_path'], 'r')
    for line in f:
        names.add(line.strip())
    f.close()
    return names

def create_twitter_auth(cf_t):
    """Function to create a twitter object
    Args: cf_t is

    Returns: Nothing
    """
    # When using twitter stream you must authorize.
    # these tokens are necessary for user authentication
    # create twitter API object

    auth = OAuth(cf_t['access_token'], cf_t['access_token_secret'], \
           cf_t['consumer_key'], cf_t['consumer_secret'])

    try:
        # create twitter API object
        twitter = Twitter(auth=auth, retry=True)
    except TwitterHTTPError:
        traceback.print_exc()
        time.sleep(cf_t['sleep_interval'])

    return twitter

def get_profiles(twitter, names, cf_t, string):
    """Function write profiles to a file with the form *data-user-profiles.json*
       Args: names is a list of names
            cf_t is a list of twitter config
       Returns: .json file containing user info
    """

    # file name for daily tracking
    dt = datetime.datetime.now()
    fn = cf_t['data_path'] +'/'+dt.strftime('%Y-%m-%d-user-profiles.json')
    with open(fn, 'w') as f:
        # If the twitter-api can't find any of the usernames listed in string, it will throw a
        # TwitterHTTPError
        try:
            # Create a subquery, looking up information about users listed in 'string'
            # twitter api-docs: https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-users-lookup
            profiles = twitter.users.lookup(screen_name = string)
            sub_start_time = time.time()

            for profile in profiles:
                print("Searching twitter for User profile: ", profile['name'])
                print("User tweets: ", profile['statuses_count'])

                # Save user info
                f.write(json.dumps(profile))
                f.write("\n")

            # Get time that the query's took
            sub_elapsed_time = time.time() - sub_start_time;

            # If the total time for the query was less than the sleep interval,
            # wait the remaining amount of time
            if(sub_elapsed_time < cf_t['sleep_interval']):
                time.sleep(cf_t['sleep_interval'] + 1 - sub_elapsed_time)
        except TwitterHTTPError:
            print("---------- No Users Found ----------")
            traceback.print_exc()
            time.sleep(cf_t['sleep_interval'])

    f.close()
    return fn

def timeline_path(screen_name, cf_t):
    return cf_t['timeline_path']+screen_name+".json"

# check the max tweet id in last round
def timeline_file_stats(screen_name, cf_t):
    stats={}
    #fn = cf_t['data_path']+"/timeline/"+screen_name+".json"
    fn =timeline_path(screen_name, cf_t)
    stats['tweet_max_id'] = -1
    stats['tweet_min_id'] = -1
    stats['total_tweets_file']=0
        
    with open(fn, 'r') as json_file:
        all_tweets = json.load(json_file)

    for tweet_id, tweet_data in all_tweets.items():

        stats['total_tweets_file'] += 1

        if(stats['tweet_min_id'] == -1):
            stats['tweet_min_id'] = int(tweet_id)

        stats['tweet_max_id'] = max(stats['tweet_max_id'], int(tweet_id))
        stats['tweet_min_id'] = min(stats['tweet_min_id'], int(tweet_id))

    return stats

def profiles_to_timelines(twitter, profiles_fn, cf_t):
    with open (profiles_fn,'r') as f:
        count=0
        for line in f:
            profile = json.loads(line)
            stats=timeline_file_stats(profile['screen_name'],cf_t)
            print('user:', profile['screen_name'],'\n    Total tweets:',   \
            profile['statuses_count'], '\n     File tweets:',stats['total_tweets_file'] )
            if stats['total_tweets_file']<profile['statuses_count']:
                tweets_remaining= profile['statuses_count']-stats['total_tweets_file']
                print("Go get some more")
                get_timeline(twitter, profile['screen_name'], cf_t, stats['tweet_max_id'],tweets_remaining)
            else:
                print("Got them all")
            count+=1
    print('Retreived tweets for ',count,' profiles.')
    return

# check the max tweet id in last round

def get_timeline(twitter, screen_name, cf_t, tweet_max,tweets_remaining):
    print ("Getting data for: ", screen_name)
    fn =timeline_path(screen_name, cf_t)
    if os.path.exists(fn):
        f = open(fn, 'a')
    else:
        f = open(fn, 'w')

    # twitter allows 180 usertimeline requests per 15 min window
    # i.e. 5 seconds interval between consecutive requests
    interval = cf_t['sleep_interval']
    count = 200
    curr_max = 0;
    prev_max = 0;
    ret = 0;

    # tracking pulled tweets so that only save unique tweets
    tweetIds = set()
    more = True
    while (more):
        results = []
        try:
            if (0 == curr_max):
                results = twitter.statuses.user_timeline(screen_name = screen_name, count = count)
                if len(results) == 0:
                    time.sleep(interval)
                    return ret;
                ret = results[0]['id']
                curr_max = results[-1]['id']
            else:
                results = twitter.statuses.user_timeline(screen_name = screen_name, count = count, max_id = curr_max)
                if len(results) == 0:
                    time.sleep(interval)
                    return ret;
                prev_max = curr_max;
                curr_max = results[-1]['id']

            if (curr_max == prev_max):
                # reach the end of all possible results
                break

            start_time = time.time();

            for status in results:
                if status['id'] not in tweetIds: # uniqueness
                    if status['id'] <= tweet_max: # already seen, no more new tweets from this point
                        more = False
                        break;

                    tweetIds.add(status['id'])
                    try:
                        f.write(json.dumps(status))
                        f.write('\n')
                    except ValueError:
                        # json parser error
                        traceback.print_exc()
                        continue

            elapsed_time = time.time() - start_time;
            if (interval + 1 - elapsed_time) > 0:
                time.sleep(interval + 1 - elapsed_time)
        except TwitterHTTPError:
            #
            traceback.print_exc()
            time.sleep(interval)
            break;
        except KeyboardInterrupt:
            f.flush()
            f.close()
            raise KeyboardInterrupt

    f.flush()
    f.close()

    print ("Got %d new tweets for %s..."%(len(tweetIds), screen_name))
    return ret
