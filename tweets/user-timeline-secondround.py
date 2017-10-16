#!/usr/bin/python

#--------------------------------------------------------------------------------------
# twitter-user-timeline 2nd round
#  - suppose the 1st round already done - some collected tweets there.
#  - pulls (up to 3200 most recent tweets) a user's current timeline.
#  - only collect tweets newer than last seen (again, up to 3200).
#--------------------------------------------------------------------------------------

from twitter import *

import sys, Queue, time, datetime, json
import traceback

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

def readUsers(fn):
    queue = Queue.Queue()

    f = open(fn, 'r')
    for line in f:
        a = line.strip().split();
        if len(a) == 0:
            continue
        user = a[-1]
        queue.put(user)

    f.close()
    return queue

# check the max tweet id in last round
def lastTweet(screenName):
  tweetId = -1;
  try:
    f = open('%s.json'%screenName, 'r')

    for line in f:
      j = json.loads(line)
      i = j['id']
      tweetId = max(tweetId, i);

    f.close()
  except IOError:
    f = open('%s.json'%screenName, 'a')
    f.close()

  return tweetId

def userTimeLine(twitter, screenName):
    print "Working on %s..."%screenName;
     
    last = lastTweet(screenName)

    f = open('%s.json'%screenName, 'a')

    # twitter allows 180 usertimeline requests per 15 min window 
    # i.e. 5 seconds interval between consecutive requests
    interval = 5  

    count = 200

    curr_max = 0;
    prev_max = 0;
    ret = 0;
    # tracking pulled tweets so that only save unique tweets
    tweetIds = set()
    more = True
    while (more):
        results = []
        try:
            if (0 == curr_max):
                results = twitter.statuses.user_timeline(screen_name = screenName, count = count)
                if len(results) == 0:
                    time.sleep(interval)
                    return ret;
                ret = results[0]['id']
                curr_max = results[-1]['id']
            else:
                results = twitter.statuses.user_timeline(screen_name = screenName, count = count, max_id = curr_max)
                if len(results) == 0:
                    time.sleep(interval)
                    return ret;
                prev_max = curr_max;
                curr_max = results[-1]['id']

            if (curr_max == prev_max): 
                # reach the end of all possible results
                break

            start_time = time.time();

            for status in results:
                if status['id'] not in tweetIds: # uniqueness
                    if status['id'] <= last: # already seen, no more new tweets from this point
                        more = False
                        break;

                    tweetIds.add(status['id'])
                    try:
                        f.write(json.dumps(status))
                        f.write('\n')
                    except ValueError:
                        # json parser error
                        traceback.print_exc()
                        continue

            elapsed_time = time.time() - start_time;
            if (interval + 1 - elapsed_time) > 0:
                time.sleep(interval + 1 - elapsed_time)
        except TwitterHTTPError:
            # 
            traceback.print_exc()
            time.sleep(interval)
            break;
        except KeyboardInterrupt:
            f.flush()
            f.close()
            raise KeyboardInterrupt

    f.flush()
    f.close()

    print "Got %d new tweets for %s..."%(len(tweetIds), screenName);
    return ret

def main(argv):
    
    # read access token and consumer key
    secrets = readSecrets('token.txt')

    # When using twitter stream you must authorize.
    # these tokens are necessary for user authentication
    # create twitter API object
    auth = OAuth(secrets['access_key'], secrets['access_secret'], secrets['consumer_key'], secrets['consumer_secret'])

    # users = readUsers(argv[1])

    # create twitter API object
    twitter = Twitter(auth = auth)

    # last recorded tweet max_id
    # all tweets older that were pulled before
    userfn = argv[1]
    users = readUsers(userfn)

    while not users.empty():
        try:
            screenName = users.get()
            mostRecentTweetId = userTimeLine(twitter, screenName)
            # will check it again
            users.put(screenName)
        except KeyboardInterrupt:
            traceback.print_exc()
            break

if __name__ == "__main__":
  main(sys.argv)
