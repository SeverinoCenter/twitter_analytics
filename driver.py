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


def get_users_from_file(config):


    return



if __name__ == '__main__':

    # Create Initial config dictionary
    cf_dict = config_init("config/config.yaml");

    print(cf_dict)

    # Get usernames from text file
    all_users = get_users_from_file(cf_dict);


    # Test if each user already exists, split into two lists
    # containing existing users and new users
    #
    # A user will exist if there is a [username].json in the /tweets/ directory


    #### EXISTING USER PROCESS ####

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
