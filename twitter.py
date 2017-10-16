#This will import some required libraries.
import sys
import ruamel.yaml
#This is your configuration file.
general_yaml='../../config/config.yaml'
with open(general_yaml, 'r') as yaml:
   cf=ruamel.yaml.round_trip_load(yaml, preserve_quotes=True)

twitter_yaml='../../config/twitter/config.yaml'
with open(twitter_yaml, 'r') as yaml_t:
   cf_t=ruamel.yaml.round_trip_load(yaml_t, preserve_quotes=True)


   #This will allow us to import some useful utilities.
if cf['docker']:
   cf_t['path']=cf['docker_path']
else:
   cf_t['path']=cf['local_path']

sys.path.append(cf_t['path']+"/twitterutils")
import importlib
import twitterutils as tu
importlib.reload(tu)
#initialize some variables.
cf_t=tu.twitter_init(cf_t)
#print(ruamel.yaml.dump(cf_g, sys.stdout, Dumper=ruamel.yaml.RoundTripDumper))



import pandas as pd
df=pd.DataFrame.from_csv(cf_t['names_path'])
df=df.drop_duplicates(subset='screen_name', keep="first")
','.join(list(df['screen_name']))
df[0:49]



s=0
for i in range(math.ceil(len(df)/50)):
    #val=','.join(list(df[s:(s+49)]))
    val=df[s:(s+49)]
    print(val)
    s+=49


import math
for loop in (math.ceil(len(df)/50)):
    print(loop)

twitter= tu.create_twitter_auth(cf_t)


#This will collect user profiles.
importlib.reload(tu)
profiles_fn=tu.get_profiles(twitter, df['screen_name'], cf_t)



print(cf_t['names_path'])
import csv
with open(cf_t['names_path'], 'r') as f:
    reader = csv.reader(f)
    names = pd.DataFrame(reader)
print(type(names))
print(names)



#profile_last_update	profile_total_tweets	timeline_last_update	timeline_total_tweets	timeline_limit	timeline_limit_date
import pandas as pd
df=pd.DataFrame.from_csv(cf_t['names_path'])
df=names.drop_duplicates(subset='screen_name', keep="first")
for index, name in df.iterrows():
    print(row['screen_name'])
