import twitterutils as tu

# import twitter
import sys
import ruamel.yaml
import pandas as pd
import math
import csv

### TODO ###
#   1. Clean code and function everything to encorporate into Airflow
#   2. Create data collection status for each profile
#     a. Look at issue #6 on gitlab
# ? 3. Get jupyterhub running locally to test everything 
#     a. Convert file to jupyter notebook
#   4. Profile pulling logic (don't pull if already have)


# Helper function to print the contents of a dictionary
def print_dict(cf_dict):
	for keys,values in cf_dict.items():
		print(keys)
		print(values)
		print("----")

# Converts usernames entered into a txt file into the proper format
# csv file
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
# PARAMS: file: Path to the config.yaml
def config_init(file):
	# Configure config files
	twitter_config = "config/config.yaml"
	with open(twitter_config, 'r') as yaml_t:
		cf_dict=ruamel.yaml.round_trip_load(yaml_t, preserve_quotes=True)

	return tu.twitter_init(cf_dict)

# Create a string containing usernames to pull multiple users at a time
def names_to_string(config):
	df = pd.read_csv(config['names_path'].replace(".txt", ".csv"))  # Create a pandas datafrom from screen_names.csv
	df = df.drop_duplicates(subset='screen_name', keep="first")  # Remove any duplicate users
	return '.'.join(list(df['screen_name']))


if __name__ == "__main__":


	# Create config dictionary
	cf_dict = config_init("config/config.yaml");

	# Convert screen_names.txt to screen_names.csv
	text_to_csv(cf_dict['names_path'])

	# Convert list of names into one string to pull multiple users in one request
	names = names_to_string(cf_dict);


	# Authorize twitter
	twitter = tu.create_twitter_auth(cf_dict)

	# Find the profiles of all the names in screen_names.txt and create a YYYY-MM-DD-user_profiles.json file
	# containing the profiles
	profiles_fn = tu.get_profiles(twitter, cf_dict['names_path'], cf_dict)

	# Create .json file for each profile
	tu.profiles_to_timelines(twitter, profiles_fn, cf_dict)
