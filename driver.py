import twitterutils as tu

# import twitter
import sys
import ruamel.yaml
import pandas as pd
import math
import csv
import json
import datetime
from os import listdir, path

##########  config_init  ##############
# Initialize the configuration file and store it in dictionary
#
# PARAMS
#        file: Path to the config.yaml
#
# RETURNS
#        Dictionary containing config info
def config_init(file):
    # Configure config files
    twitter_config = "config/config.yaml"
    with open(twitter_config, 'r') as yaml_t:
        cf_dict=ruamel.yaml.round_trip_load(yaml_t, preserve_quotes=True)

    return tu.twitter_init(cf_dict)


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
    users_file = open(config['path'] + config['config'] + '/' + config['file'], 'r')

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
    users_path = config['path'] + '/tweets/';

    # Traverse over tweets directory
    for file in listdir(users_path):
        # Make sure the current file is a users timeline
        if(file.endswith(".json")):
            current_name = path.splitext(file)[0].lower()
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
    with open(config['path'] + '/user_stats.json', 'r') as stats_file:
        all_info = json.load(stats_file)[user]
    return all_info


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
    user_info_new = twitter.users.lookup(screen_name = user)
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


    users_path = config['data_path']
    # Traverse over YYYY-MM-DD-user-profiles.json files
    for date_file in listdir(users_path):
        # Safety check incase there are non user files in directory
        if(date_file.endswith(".json") == False):
            continue

        lpDT = date_file[0:10] # Get the date from the name of the file
        date_file = users_path + "/" + date_file
        with open(date_file, 'r') as d_file:

            # Traverse over each user profile information
            for line in d_file:
                # Get twitter json dump
                user_info = json.loads(line)

                # Make sure the correct user is being used
                if(user_info['screen_name'] != user):
                    continue
                else:
                    stats['user_id'] = user_info['id']
                    # Makes sure to keep the latest date instead of most recently accessed
                    if( compare_dates(lpDT, stats['date_last_pull']) ):
                        stats['date_last_pull'] = lpDT
                    stats['tweets_last_pull'] = user_info['statuses_count']


    with open(config['path'] + '/user_stats.json', 'r') as stats_file:
        file_data = json.load(stats_file)
        file_data[user] = stats

    json.dump(file_data, open(config['path'] + '/user_stats.json', 'w'), indent=4)


    return 0



if __name__ == '__main__':
    # Create Initial config dictionary
    cf_dict = config_init("config/config.yaml")
    twitter = tu.create_twitter_auth(cf_dict)
    # print(cf_dict)

    # Get usernames from text file
    all_users = get_all_users_from_file(cf_dict)

    #### EXISTING USER PROCESS ####
    for user in all_users['existing']:
        user_info_new = twitter.users.lookup(screen_name = user)
        # Get true twitter screen_name
        true_name = user_info_new[0]['screen_name']

        # Find number of new tweets
        num_new = check_for_new_tweets(cf_dict, true_name, twitter)


        # create_user_stats(cf_dict, true_name)

        # No new tweets since last info pull
        num_new = 0
        if(num_new == 0):
            print("No new tweets detected for", user)
            print("Continuing to next user")
            continue;

        # New tweets since last pull
        else:
            print(num_new, "new tweets detected for", user)

            if(num_new < 200):
                print("    Pulling newest tweets")
                user_max_id = get_user_stats(cf_dict, true_name)['tweet_max_id']
                # Pull new tweets in one go and add to file
                new_tweets = twitter.statuses.user_timeline(screen_name = true_name,
                                                               since_id = user_max_id)
            else:
                print("    Paging through new tweets")
                # Page through new tweets and add to file

        # Update user_stats with relevant information

    #### NEW USER PROCESS ####
    for user in all_users['new']:
        # Get true twitter screen_name
        user_info_new = twitter.users.lookup(screen_name = user)
        true_name = user_info_new[0]['screen_name']

        # see total tweets
        num_tweets = check_for_new_tweets(cf_dict, true_name, twitter)


        num_tweets = 0;
        if(num_tweets > 2000):
            print("    Paging through timeline")
            # page through timeline 200 at a time, storing all tweets
            # in [username].json

        else:
            print("    Pulling timeline in one")
            # get entire timeline and store
            tweets = twitter.statuses.user_timeline(screen_name = true_name)

        user_file = cf_dict['path'] + '/tweets/' + true_name + ".json"
        with open(user_file, 'w') as user_file:
            for tweet in tweets:
                user_file.write(json.dumps(tweet))
                user_file.write("\n")


        # create user_stat
        # create_user_stats(cf_dict, true_name)
