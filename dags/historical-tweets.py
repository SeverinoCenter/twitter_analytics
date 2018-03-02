#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
for each screen name, get his tweets information
'''

import csv, codecs
import sys, re
import os.path
import json
from dateutil import parser

# map screen name to owner
def readUOI(fn):
  ret = {}

  f = open(fn, 'r')
  for line in f:
    a = line.strip().split()
    assert(len(a) == 2)
    ret[a[1]] = a[0]
  f.close()

  return ret

# parse tweets by a specific account 
def read_historical_tweets(sname, owner, tweetwriter, retweetwriter):
  fn = '%s.json'%sname
  # check if the file exist
  if not os.path.isfile(fn):
    return

  f = open(fn, 'r')

  writer = tweetwriter
  for line in f:
    ret = []
    status = json.loads(line)

    if parser.parse(status['created_at']).year > 2014:
      continue

    # separate retweet and tweet into different files
    if 'retweeted_status' in status:
      writer = retweetwriter
    else:
      writer = tweetwriter

    # A. Company/owner
    ret.append(owner)

    #B. text 
    ret.append(status['text'].encode('utf-8'))

    #C. favorite 
    ret.append(status['favorited'])

    #D. favoriteCount 
    ret.append(status['favorite_count'])

    #E. replyToSN 
    ret.append(status['in_reply_to_screen_name'])

    #F. created 
    ctime = parser.parse(status['created_at']).strftime('%Y-%m-%d %H:%M:%S')
    ret.append(ctime)

    #G. truncated  
    ret.append(status['truncated'])

    #H. replyToSID
    ret.append(status['in_reply_to_status_id'])

    #I. id 
    ret.append(status['id'])

    #J. replyToUID 
    ret.append(status['in_reply_to_user_id'])

    #K. statusSource 
    p = re.compile(r'<.*?>')
    source = p.sub('', status['source'])
    ret.append(source.encode('utf-8'))

    #L. screenName
    ret.append(status['user']['screen_name'].encode('utf-8'))

    #M. retweetCount
    ret.append(status['retweet_count'])

    #N. isRetweet 
    if 'retweeted_status' in status:
      ret.append(True)
    else:
      ret.append(False)

    #O. retweeted 
    ret.append(status['retweeted'])

    if status['geo']:
        #P. longitude 
        ret.append(status['geo']['coordinates'][1])
        #Q. latitude
        ret.append(status['geo']['coordinates'][0])
    else:
        ret.append(None)
        ret.append(None)

    #R. Additionally, we will collect the number of hashtags each tweet/retweet contains
    count = 0;
    for hashtag in status['entities']['hashtags']:
        count += 1
    ret.append(count)

    writer.writerow(ret)
  f.close()

# main
def main(argv):
  fn = argv[1]
  uoi = readUOI(fn) 

  tweetfile = file("historical-tweets.csv", "w")
  tweetwriter = csv.writer(tweetfile)

  retweetfile = file("historical-retweets.csv", "w")
  retweetwriter = csv.writer(retweetfile)

  header = ["Owner", "Text", "Favorite", "favoriteCount", "replyToSN", "created", "truncated", "replyToSID", "id", "replyToUID", "statusSource", "screenName", "retweetCount", "isRetweet", "retweeted", "longitude", "latitude", "numHashtags"]
  tweetwriter.writerow(header)
  retweetwriter.writerow(header) 

  for name in uoi:
    read_historical_tweets(name, uoi[name], tweetwriter, retweetwriter)

  tweetfile.close()
  retweetfile.close()

if __name__ == "__main__":
  main(sys.argv)
