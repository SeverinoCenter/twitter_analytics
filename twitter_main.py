import twitterutils as tu

# import twitter
import sys
import ruamel.yaml
import pandas as pd
import math
import csv




if __name__ == "__main__":

	# Configure config files
	twitter_config = "config/config.yaml"
	with open(twitter_config, 'r') as yaml_t:
		cf_dict=ruamel.yaml.round_trip_load(yaml_t, preserve_quotes=True)

	cf_dict = tu.twitter_init(cf_dict)
	
	print(ruamel.yaml.dump(cf_dict, sys.stdout, Dumper=ruamel.yaml.RoundTripDumper))
	df = pd.DataFrame.from_csv(cf_dict['names_path'])
	df = df.drop_duplicates(subset='screen_name', keep="first")
	# '.'.join(list(df['screen_name']))
	# df[0:49]


	# s=0
	# for i in range(math.ceil(len(df)/50)):
	# 	val=df[s:(s+49)]
	# 	print(val)
	# 	s+=49


	# for loop in (math.ceil(len(df)/50)):
	# 	print(loop)

	# twitter = tu.create_twitter_auth(cf_dict)

	# profiles_fn = tu.get_profiles(twitter, df['screen_name'], cf_t)


	# print(cf_t['names_path'])
	# with open(cf_t['names_path'], 'r') as f:
	#     reader = csv.reader(f)
	#     names = pd.DataFrame(reader)
	# print(type(names))
	# print(names)