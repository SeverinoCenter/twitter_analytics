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
            if(current_name == name): 
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
    return all_info[0]


#######  check_for_new_tweets ############
# Checks to see if there are any new tweets by a specific user
#
# PARAMS
#       config: Main configuration dict
#       user: username of user in question
#       twitter: Twitter api reader
#
# RETURNS
#       num_tweets: Number of new tweets ( >= 0)
def check_for_new_tweets(config, user, twitter):
    num_tweets = 0;
    user_info_new = twitter.users.lookup(screen_name = user)

    # Get true twitter screen_name
    user_true_name = user_info_new[0]['screen_name']
    user_info_file = get_user_stats(config, user)

    num_tweets = user_info_new[0]['statuses_count'] - user_info_file['lpTweetFile']

    return num_tweets



if __name__ == '__main__':

    # Create Initial config dictionary
    cf_dict = config_init("config/config.yaml")
    twitter = tu.create_twitter_auth(cf_dict)
    # print(cf_dict)

    # Get usernames from text file
    all_users = get_all_users_from_file(cf_dict)

    #### EXISTING USER PROCESS ####

    for user in all_users['existing']:
        # Find number of new tweets
        num_new = check_for_new_tweets(cf_dict, user, twitter)
        # print(user, num_new)

        # No new tweets since last info pull
        if(num_new == 0):
            print("No new tweets detected for", user)
            print("Continuing to next user")
            continue;

        # New tweets since last pull
        else:
            print(num_new, "new tweets detected for", user)

            if(num_new < 200):
                print("    Pulling newest tweets")
                # Pull new tweets in one go and add to file
            else:
                print("    Paging through new tweets")
                # Page through new tweets and add to file

            # Update user_stats with relevant information

    #### NEW USER PROCESS ####

    for user in all_users['new']:
        # see total tweets
        num_tweets = check_for_new_tweets(cf_dict, user, twitter)

        if(num_tweets > 2000):
            print("    Paging through timeline")
            # page through timeline 200 at a time, storing all tweets
            # in [username].json

        else:
            print("    Pulling timeline in one")
            # get entire timeline and store
            # create user_stat