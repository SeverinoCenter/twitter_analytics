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

############################### TODO ######################################
##     1. Clean code and function everything to encorporate into Airflow
##     2. Create data collection status for each profile
##       a. Look at issue #6 on gitlab
##
##  	username | date of last pull | num of tweets in last pull | num of tweets in file | num of tweets that can't access | max tweetid | min tweetid
##     usrID | lpDT | lpTWC | lpTWF | ntwCA | mxTWI | mnTWI
##
##   ? 3. Get jupyterhub running locally to test everything
##       a. Convert file to jupyter notebook
##     4. Profile pulling logic (don't pull if already have)
##########################################################################


# Helper to compare two date strings in format of 'YYYY-MM-DD'
# Converts the dates into ints with the format YYYYMMDD
# This allows easy comparing by using integer logic
#
# PARAMS
#    	date1: First date to be compared
# 		date2: Second date to be compared
#
# RETURNS
#		True: date1 > date2 (date1 is more recent than date2)
#		False: date1 < date2 (date2 is more recent than date1)
def compare_dates(date1, date2):
	# Convert date1 to int
	date1 = date1.replace('-', '')
	date1_int = int(date1)

	# Convert date2 to int
	date2 = date2.replace('-', '')
	date2_int = int(date2)

	return date1_int > date2_int


# Get all the necessary statistics for a single user
#
# PARAMS
#		screenname: String containing the screen_name of the user in question
# 		config: Dictionary containing all the configuration info
#
# RETURNS
#		user_stats: Dictionary containing the necessary user stats
def gather_user_stats(screenname, config):
	# Generate the paths for the specific user
	users_path = config["data_path"]


	# Initialize return dict with initial values
	user_stats = { 'screen_name': screenname,
				   'user_id': -1,
	 			   'date_last_pull': "0000-00-00",            # Date of last pull
	 			   'tweets_last_pull': -1,		# Number of tweets in last pull
	 			   'num_tweet_file': -1,		# number of tweets on file
	 			   'max_tweet_id': -1,		# Number of tweets that can't access
	 			   'min_tweet_id': -1 }

	# Get maxTweetID, minTweetID, lpTweetFile
	partial_stats = tu.timeline_file_stats(screenname, config)
	user_stats['num_tweet_file'] = partial_stats['total_tweets_file']
	user_stats['max_tweet_id'] = partial_stats['tweet_max_id']
	user_stats['min_tweet_id'] = partial_stats['tweet_min_id']

	# Traverse over YYYY-MM-DD-user-profiles.json files
	for date_file in listdir(users_path):

		# Safety check incase there are non user files in directory
		if(date_file.endswith(".json") == False):
			continue

		lpDT = date_file[0:10] # Get the date from the name of the file
		date_file = users_path + "/" + date_file
		with open(date_file, 'r') as file:

			# Traverse over each user profile information
			for line in file:
				# Get twitter json dump
				user_info = json.loads(line)

				# Make sure the correct user is being used
				if(user_info['screen_name'] != screenname):
					continue
				else:
					user_stats['userID'] = user_info['id']
					# Makes sure to keep the latest date instead of most recently accessed
					if( compare_dates(lpDT, user_stats['date_last_pull']) ):
						user_stats['date_last_pull'] = lpDT
					user_stats['tweets_last_pull'] = user_info['statuses_count']
	return user_stats

# Create a csv file containing the stats for every user in the /tweets directory
#
# PARAMS
#		config: Dictionary containing the config info
#
# RETURNS
#		NA
def create_user_stats(twitter, config):
	# tweets_path = config['data_path'].replace("profiles", "tweets/")
	#
	# # Create a list of users on file
	# users = []
	# for file in listdir(tweets_path):
	# 	if(file.endswith(".json") == False):
	# 		continue
	# 	users.append(path.splitext(file)[0])

	users_file = open(config['names_path'], 'r')

	# Create a list of users on file
	users = []

	for line in users_file:
		user_info_new = twitter.users.lookup(screen_name = line)

		# Get true twitter screen_name
		user_true_name = user_info_new[0]['screen_name']

		users.append(user_true_name.strip("\n"))

	numUsers = len(users)

	# Dictionary containing user info
	data = {}

	x = 0;
	# Add all users to dictionary with their stats

	while(x<numUsers):
		print(users[x])
		u_stats = gather_user_stats(users[x], config)
		print(u_stats)
		data[users[x]] = []
		data[ users[x] ].append( u_stats )
		x += 1

	with open('user_stats.json', 'w') as outfile:
		json.dump(data, outfile, indent=4, sort_keys=True)


# Converts usernames entered into a txt file into the proper format
# csv file
#
# PARAMS
#		file: String containing path to the screen_names.txt file
#
# RETURNS
#		NA
def text_to_csv(file):
	csv_file = file.replace(".txt", ".csv") # Create the name of the csv file

	# Create csv file and write header
	csv_file = open(csv_file, 'w')
	writer = csv.writer(csv_file) # create csv object to write to the csv
	header = ["index", "screen_name"]
	writer.writerow(header)

	txt_file = open(file, 'r')

	count = 1
	for line in txt_file:
		row = [ str(count), line.strip('\n') ]  # Create python dict so csv correctly writes
		count += 1;
		writer.writerow(row)

# Initialize the configuration file and store it in dictionary
#
# PARAMS
#		file: Path to the config.yaml
#
# RETURNS
#		Dictionary containing config info
def config_init(file):
	# Configure config files
	twitter_config = "/usr/local/airflow/dags/config/config.yaml"
	with open(twitter_config, 'r') as yaml_t:
		cf_dict=ruamel.yaml.round_trip_load(yaml_t, preserve_quotes=True)

	return tu.twitter_init(cf_dict)

# Create a comma seperated string containing usernames to pull multiple users at a time
#
# PARAMS
#		config: Dictionary containing config info
#
# RETURNS
#		Single string containing all the names in screen_names.csv; comma seperated
def names_to_string(config):
	df = pd.read_csv(config['names_path'].replace(".txt", ".csv"))  # Create a pandas datafrom from screen_names.csv
	df = df.drop_duplicates(subset='screen_name', keep="first")  # Remove any duplicate users
	return ','.join(list(df['screen_name']))

def main():
	# Create config dictionary
	cf_dict = config_init("config/config.yaml");

	# Convert screen_names.txt to screen_names.csv
	text_to_csv(cf_dict['names_path'])

	# # Convert list of names into one string to pull multiple users in one request
	names = names_to_string(cf_dict);

	# # Authorize twitter
	twitter = tu.create_twitter_auth(cf_dict)

	# # Find the profiles of all the names in screen_names.txt and create a YYYY-MM-DD-user_profiles.json file
	# # containing the profiles
	profiles_fn = tu.get_profiles(twitter, cf_dict['names_path'], cf_dict, names)

	# # Create .json file for each profile
	tu.profiles_to_timelines(twitter, profiles_fn, cf_dict)

	create_user_stats(twitter, cf_dict)


if __name__ == "__main__":
    main()