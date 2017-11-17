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
#		file: Path to the config.yaml
#
# RETURNS
#		Dictionary containing config info
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
            if(current_name == name): return True

    # User not found
    return False

#######  check_for_new_tweets ############
# Checks to see if there are any new tweets by a specific user
#
# PARAMS
#       cf_dict: Main configuration dict
#       user: username of user in question
#
# RETURNS
#       num_tweets: Number of new tweets ( >= 0)
def check_for_new_tweets(config, user):
    num_tweets = 0;



    return num_tweets



if __name__ == '__main__':

    # Create Initial config dictionary
    cf_dict = config_init("config/config.yaml");

    # print(cf_dict)

    # Get usernames from text file
    all_users = get_all_users_from_file(cf_dict);

    #### EXISTING USER PROCESS ####

    for user in all_users['existing']:
        
        num_new = check_for_new_tweets(cf_dict, user)

    # FOREACH USER

    # Get latest tweet ID from Profile (latest_tweet_profile)

    # If  latest_tweet_file == latest_tweet_profile
    # No new tweets, go to next userID

    # ELSE figure out how many new tweets there are

    # If new tweets < 200 pull newest tweets in one go
    # and add to [username].json

    # ELSE page through new tweets 100 at a time
    # and add each page to [username].json

    # Update user_stats with new max_tweetID and other relevent info



    #### NEW USER PROCESS ####

    # See how many total tweets they have

    # If tweet_count > 2000

    # Page through tweets 200 at a time, storing each page in
    # [username].json

    # ELSE tweet_count < 2000

    # Get entire timeline in one pull and store it in
    # [username].json

    # Create user_stat info and store in existing user_stat
