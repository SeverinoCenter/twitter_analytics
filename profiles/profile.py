#!/usr/bin/python

#-----------------------------------------------------------------------
# profile collection
#  - given screen names get profiles for them
#-----------------------------------------------------------------------

import sys, json, time
import datetime, traceback
import Queue
from twitter import *

_path = "/home/lux4/WangFang/user_profile"

# read token file
def readSecrets( fn ):
    ret = dict()
    secrets = open( fn, 'r' )
    for line in secrets:
        line = line.strip();
        # ignore empty and comment lines
        if len(line) == 0:
            continue;
        if line[0] == '#':
            continue;
        a = line.split();
        assert(len(a) == 2)
        ret[a[0]] = a[1];
    secrets.close();
    return ret;

# read user list
def readUsers(fn):
    f = open(fn, 'r')
    ret = []

    for line in f:
        a = line.strip().split();
        user = a[-1]
        ret.append(user)

    f.close()
    return ret;

def collect(_names, secrets):

    # When using twitter stream you must authorize.
    # these tokens are necessary for user authentication
    # create twitter API object
    auth = OAuth(secrets['access_key'], secrets['access_secret'], secrets['consumer_key'], secrets['consumer_secret'])

    # create twitter API object
    twitter = Twitter(auth = auth) 
 
    # twitter api access limit 
    # Requests / 15-min window (user auth) 180 => 5 sec/request
    interval2 = 5

    # file name for daily tracking
    file_dt = datetime.datetime.now()
    filename = file_dt.strftime('%Y-%m-%d-user-profiles.json')
    w_profile = open("%s/%s"%(_path, filename), 'w')

    # now we loop through them to pull out more info, in blocks of 100.
#    for n in range(0, len(_names), 100):
#        names = _names[n:n+100]
    for names in _names:
        print names
        try:
            # create a subquery, looking up information about these users
            # twitter API docs: https://dev.twitter.com/docs/api/1/get/users/lookup
            subquery = twitter.users.lookup(screen_name = names)
            sub_start_time = time.time()

            for user in subquery:
                # now save user info
                w_profile.write(json.dumps(user))
                w_profile.write("\n")

            sub_elapsed_time = time.time() - sub_start_time;
            if sub_elapsed_time < interval2:
                time.sleep(interval2 + 1 - sub_elapsed_time)
        except TwitterHTTPError:
            traceback.print_exc()
            time.sleep(interval2)
            continue

    w_profile.close()

def main(argv):

    # read access token and consumer key
    secrets = readSecrets('%s/token.txt'%_path)

    # read user screen name
    names = readUsers('%s/screenNames.txt'%_path)

    collect(names, secrets)

    print "Done!"

if __name__ == "__main__":
    main(sys.argv)
