import twitterutils as tu

import sys
import ruamel.yaml
import pandas as pd
import math
import csv
import json
import datetime
import time
import os
import traceback
from twitter import *

##########  config_init  ##############
# Initialize the configuration file and store it in dictionary
#
# PARAMS
#        file: Path to the config.yaml
#
# RETURNS
#        Dictionary containing config info
def config_init(config_file):
    # Configure config files
    with open(config_file, 'r') as yaml_t:
        cf_dict=ruamel.yaml.round_trip_load(yaml_t, preserve_quotes=True)

    #cf_dict['path']          = os.getcwd()
    cf_dict['names_path']    = cf_dict['config'] + "/" + cf_dict['file']
    cf_dict['timeline_path'] = cf_dict['data'] + "/tweets/"
    cf_dict['profile_path']  = cf_dict['data'] + "/profiles/"

    return cf_dict


#########  get_all_users_from_file  #############
# Read the users in screen_names.txt and store them in a
# dictionary splitting the users between existing and new users
#
# PARAMS
#       config: Dictionary containing all the config info for project
#
# RETURNS
#       all_users: dictionary containing existing users and new users
def get_all_users_from_file(config):
    users_file = open(config['config'] + '/' + config['file'], 'r')

    all_users = { 'existing': [],
                       'new': [] }

    for line in users_file:
        username = line.strip()

        if(user_exists(config, username)):
            all_users['existing'].append(username)
        else:
            all_users['new'].append(username)

    return all_users


########  user_exists  ##########
# Simple helper to test if a specific user already exists in the database
#
# PARAMS
#       name: String containing the user in question
#
# RETURNS
#       True: Users exists in database
#       False: User doesnt exist
def user_exists(config, name):
    users_path = config['timeline_path']

    # Traverse over tweets directory
    for file in os.listdir(users_path):
        # Make sure the current file is a users timeline
        if(file.endswith(".json")):
            current_name = os.path.splitext(file)[0].lower()
            # User found
            if(current_name == name.lower()):
                return True

    # User not found
    return False

#######  get_user_stats #########
# Get an individual users stats from the user_stats.json file
#
# PARAMS
#        config: Main configuration dict
#        user: screenname of user in question
#
# RETURNS
#        stats: Dictionary containing the user stats
def get_user_stats(config, user):
    # Open the stats file and load the json data for the specific user

    with open(config['data'] + '/user_stats.json', 'r') as stats_file:

        all_info = json.load(stats_file)
        if user in all_info:
            print("User stats found ...")
            user_info = all_info[user]
        else:
            print("User stats not found ...")
            user_info = process_existing_tweets(config, user)
    return user_info

###### process_existing_tweets ######
# Create a user_stats.json entry for a new user that has an existing dataset in
# the form of a user_name.json file
#
# PARAMS
#       config: Main config dict
#       user: Screenname of user
#
# RETURNS
#       user_info: Dictionary containing the same info that is in the
#                   user_stats.json file
def process_existing_tweets(config, user):
    file_path = config['timeline_path'] + user + '.json'
    user_info = {
        "screen_name": user,
        "user_id": 0,
        "date_last_pull": "0000-00-00",
        "tweets_last_pull": 0,
        "max_tweet_id": -1,
        "min_tweet_id": -1,
        "num_tweet_file": 0
    }
    
    with open(file_path) as json_file:
        all_tweet_data = json.load(json_file)
        
        for tweet_id, tweet_data in all_tweet_data.items():
            # Increment number of tweets
            user_info['num_tweet_file'] += 1
    
            # Find new max_tweet_id and min_tweet_id
            if(user_info['min_tweet_id'] == -1):
                user_info['min_tweet_id'] = int(tweet_id)
    
            user_info['max_tweet_id'] = max(user_info['max_tweet_id'], int(tweet_id))
            user_info['min_tweet_id'] = min(user_info['min_tweet_id'], int(tweet_id))
    
            # Set user_id
            user_info['user_id'] = tweet_data['user']['id']
            user_info['tweets_last_pull'] = tweet_data['user']['statuses_count']

    return user_info

#######  check_for_new_tweets ############
# Checks to see if there are any new tweets by a specific user
#
# PARAMS
#       config: Main configuration dict
#       user: screenname of user in question
#       twitter: Twitter api reader
#
# RETURNS
#       num_tweets: Number of new tweets ( >= 0)
def check_for_new_tweets(config, user, twitter):
    # Get latest user info from twitter
    try:
        user_info_new = twitter.users.lookup(screen_name = user)
    except TwitterHTTPError:
        traceback.print_exc()
        time.sleep(config['sleep_interval'])

    # Get information on the user from the stats file
    user_info_file = get_user_stats(config, user)
    # Return the difference between the two
    return user_info_new[0]['statuses_count'] - user_info_file['tweets_last_pull']

######### compare_dates #########
# Helper to compare two date strings in format of 'YYYY-MM-DD'
# Converts the dates into ints with the format YYYYMMDD
# This allows easy comparing by using integer logic
#
# PARAMS
#        date1: First date to be compared
#         date2: Second date to be compared
#
# RETURNS
#        True: date1 > date2 (date1 is more recent than date2)
#        False: date1 < date2 (date2 is more recent than date1)
def compare_dates(date1, date2):
    # Convert date1 to int
    date1 = date1.replace('-', '')
    date1_int = int(date1)

    # Convert date2 to int
    date2 = date2.replace('-', '')
    date2_int = int(date2)

    return date1_int > date2_int

# Add elements of dict_2 to dict_1
#
# PARAMS
#       dict_1: Dictionary to have elements added to it
#       dict_2: Dictionary containing the elements to be added
#
# RETURNS
#       dict_1: Updated dict with items added
def update_dict(dict_1, dict_2):
    for key, value in dict_2.items():
        dict_1[key] = value

    return dict_1


######## create_user_stats ########
# Creates an entry in the user_stats file containing the requsted user info
#
# PARAMS
#       config: Main config file
#       user: screenname of user
#
# RETURNS
#       0: User stats successfully written
#       1: Something went wrong in user stats
def create_user_stats(config, user):
    # Create stats dictionary
    stats = {}

    initial_stats = tu.timeline_file_stats(user, config)
    stats['screen_name'] = user
    stats['user_id'] = -1
    stats['date_last_pull'] = "0000-00-00"
    stats['tweets_last_pull'] = -1
    stats['max_tweet_id'] = initial_stats['tweet_max_id']
    stats['min_tweet_id'] = initial_stats['tweet_min_id']
    stats['num_tweet_file'] = initial_stats['total_tweets_file']


    users_path = config['profile_path']
    # Traverse over YYYY-MM-DD-user-profiles.json files
    for date_file in os.listdir(users_path):
        # Safety check incase there are non user files in directory
        if(date_file.endswith(".json") == False):
            continue

        lpDT = date_file[0:10] # Get the date from the name of the file
        date_file = users_path + "/" + date_file


        all_file_info = json.load(open(date_file))


        user_file_info = all_file_info[user]

        # Set the user ID
        stats['user_id'] = user_file_info['id']

        # Make sure to keep the latest date instead of most recently accessed
        if( compare_dates(lpDT, stats['date_last_pull']) ):
            stats['date_last_pull'] = lpDT

        # Only update statuses count if it has increased
        if( user_file_info['statuses_count'] > stats['tweets_last_pull'] ):
            stats['tweets_last_pull'] = user_file_info['statuses_count']


    stats_path = config['data'] + "/user_stats.json"

    if(os.path.isfile(stats_path) and os.access(stats_path, os.R_OK)):
        # user_stats.json exists and is readable
        with open(stats_path, 'r') as stats_file:
            file_data = json.load(stats_file)
            file_data[user] = stats

    else:
        # user_stats.json doesn't exist
        with open(stats_path, 'w') as stats_file:
            file_data = {}
            file_data[user] = stats

    json.dump(file_data, open(config['data'] + '/user_stats.json', 'w'), indent=4)


    return 0

######### to_str ########
# Concatenates values in dictionary into a comma seperated string
#
# PARAMS
#       in_dict: Dictionary containing values to be concatenated
#
# RETURNS
#       names: String containing all values in keys
def to_str(in_dict):
    names = []

    for key, value in in_dict.items():
        arg_count = 0
        name_count = 0

        for name in value:
            if(name_count == 0):
                names.append(name + ',')
            else:
                names[arg_count] += name + ','

            name_count += 1

            if(name_count == 50):
                names[arg_count].rstrip(',')
                name_count = 0
                arg_count += 1

    return names


######### create_profile_stats ###########
# Generates/Modifies the YYYY-MM-DD-user-profiles.json file for users entered
# in the text file
#
# PARAMS
#       cf_dict: Config dict containing environment variables
#       all_users: Dictionary containing the users
#
# RETURNS
#       fn: String containing the full path of the generated/modified file
def create_profile_stats(twitter, cf_dict, all_users):

    names = to_str(all_users)


    dt = datetime.datetime.now()
    fn = cf_dict["profile_path"] + dt.strftime('%Y-%m-%d-user-profiles.json')

    all_user_info = {}
    with open(fn, 'w') as f:
        # Create a subquery, looking up information about users listed in 'string'
        # twitter api-docs: https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-users-lookup
        for name_set in names:
            try:
                profiles = twitter.users.lookup(screen_name = name_set)
                sub_start_time = time.time()

                for profile in profiles:
                    print("Searching twitter for User profile: ", profile['name'])
                    print("User tweets: ", profile['statuses_count'])

                    # Save user info
                    # f.write(json.dumps(profile))
                    # f.write("\n")
                    all_user_info[profile['screen_name']] = profile

                    # Get time that the query's took
                    sub_elapsed_time = time.time() - sub_start_time;

                    # If the total time for the query was less than the sleep interval,
                    # wait the remaining amount of time
                    if(sub_elapsed_time < cf_dict['sleep_interval']):
                        time.sleep(cf_dict['sleep_interval'] + 1 - sub_elapsed_time)
            except TwitterHTTPError:
                print('\n-----------------\n')
                traceback.print_exc()
                time.sleep(cf_dict['sleep_interval'])
        f.write(json.dumps(all_user_info, sort_keys=True, indent=1))
    return fn

def create_timelines(twitter, cf_dict, all_users):


    #### EXISTING USER PROCESS ####
    for user in all_users['existing']:

        print("Processing existing user", user)

        try:
            user_info_new = twitter.users.lookup(screen_name = user)
        except TwitterHTTPError:
            traceback.print_exc()
            time.sleep(cf_dict['sleep_interval'])

        # Get true twitter screen_name
        true_name = user_info_new[0]['screen_name']

        # Find number of new tweets
        num_new = check_for_new_tweets(cf_dict, true_name, twitter)

        tweets_found = True



        # No new tweets since last info pull
        # num_new = 0
        if(num_new == 0):
            print("    No new tweets detected for", true_name)
            tweets_found = False

        # New tweets since last pull
        elif(num_new < 200):
            print(num_new, "new tweets detected for", true_name)
            user_max_id = get_user_stats(cf_dict, true_name)['max_tweet_id']

            print("    Pulling newest tweets")

            # Pull new tweets in one go and add to file
            tweets = twitter.statuses.user_timeline(screen_name = true_name,
                                                       since_id = user_max_id,
                                                    include_rts = True)

        else:
            print("    Paging through new tweets")
            # Page through new tweets and add to file

            # Get the first page to create a max_id Number
            tweets = twitter.statuses.user_timeline(screen_name = true_name,
                                                       since_id = user_max_id,
                                                          count = 200,
                                                    include_rts = True)

            temp_max_id = tweets[-1]['id']
            num_pulled = len(tweets)
            while num_pulled != 0:
                temp_len = len(tweets)
                tweets += twitter.statuses.user_timeline(screen_name = true_name,
                                                            since_id = user_max_id,
                                                               count = 200,
                                                              max_id = temp_max_id,
                                                         include_rts = True)
                # Get the number of tweets pulled to get the last ID
                num_pulled = len(tweets) - temp_len;
                temp_max_id = tweets[-1]['id'] - 1

        if(tweets_found):
            # Add new tweets to file
            user_file = cf_dict['timeline_path'] + true_name + '.json'

            # Save the current data in file
            with open(user_file, 'r') as original:
                data = original.read()

            write_file = open(user_file, 'r+')
            all_tweets = {}
            for tweet in tweets:
                all_tweets[tweet['id']] = tweet

            write_file.write(json.dumps(all_tweets, sort_keys=True, indent=1))

            write_file.write(data)
            write_file.close()

            print("    Pulled", len(tweets), "new tweets for user", true_name)



            # Update user_stats with relevant information
            create_user_stats(cf_dict, true_name)

    #### NEW USER PROCESS ####
    for user in all_users['new']:
        # Get true twitter screen_name


        print("Processing new user", user)

        try:
            user_info_new = twitter.users.lookup(screen_name = user)
        except TwitterHTTPError:
            print("User was not found/does not exist.....sleeping")
            time.sleep(cf_dict['sleep_interval'])
            continue

        if(user_info_new[0]['protected'] == True):
            continue

        true_name = user_info_new[0]['screen_name']

        # see total tweets
        num_tweets = user_info_new[0]['statuses_count']


        tweets_found = True

        if(num_tweets == 0):
            print("No tweets detected for ", true_name)
            tweets_found = False

        elif(num_tweets > 200):
            print(num_tweets, " tweets detected for ", true_name)
            print("    Paging through timeline")
            # page through timeline 200 at a time, storing all tweets
            # in [username].json

            # Get the first page to create a max_id Number
            tweets = twitter.statuses.user_timeline(screen_name = true_name,
                                                          count = 200,
                                                    include_rts = True)

            temp_max_id = tweets[-1]['id']
            num_pulled = len(tweets)
            while num_pulled != 0:
                temp_len = len(tweets)
                tweets += twitter.statuses.user_timeline(screen_name = true_name,
                                                               count = 200,
                                                              max_id = temp_max_id,
                                                         include_rts = True)
                # Get the number of tweets pulled to get the last ID
                num_pulled = len(tweets) - temp_len
                temp_max_id = tweets[-1]['id']-1

        else:
            print(num_tweets, " tweets detected for ", user)
            print("    Pulling timeline in one")
            # get entire timeline and store
            tweets = twitter.statuses.user_timeline(screen_name = true_name,
                                                          count = num_tweets,
                                                    include_rts = True)


        if(tweets_found):
            user_file = cf_dict['timeline_path'] + true_name + '.json'
            write_file = open(user_file, 'w')
            # Loop through each tweet and write it to the file
            all_tweets = {}
            for tweet in tweets:
                all_tweets[tweet['id']] = tweet

            write_file.write(json.dumps(all_tweets, sort_keys=True, indent=1))

            write_file.close()

            # create user_stat
            create_user_stats(cf_dict, true_name)


def main():
    # Create Initial config dictionary
    cf_dict = config_init("dags/config/config.yaml")
    twitter = tu.create_twitter_auth(cf_dict)

    # Get usernames from text file
    all_users = get_all_users_from_file(cf_dict)

    # create_profile_stats(twitter, cf_dict, all_users)

    create_timelines(twitter, cf_dict, all_users)

if __name__ == '__main__':
    main()
