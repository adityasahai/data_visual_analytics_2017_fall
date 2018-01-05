import csv
import json
import time
import tweepy


# You must use Python 2.7.x
# Rate limit chart for Twitter REST API - https://dev.twitter.com/rest/public/rate-limits

def loadKeys(key_file):
    # put your keys and tokens in the keys.json file,
    #       then implement this method for loading access keys and token from keys.json
    # rtype: str <api_key>, str <api_secret>, str <token>, str <token_secret>
    with open(key_file) as keys_fd:
        keys = json.load(keys_fd)    

    return keys['api_key'],keys['api_secret'],keys['token'],keys['token_secret']

# Q1.b.(i) - 5 points
def getPrimaryFriends(api, root_user, no_of_friends):
    # TODO: implement the method for fetching 'no_of_friends' primary friends of 'root_user'
    # rtype: list containing entries in the form of a tuple (root_user, friend)
    primary_friends = []
    TIMER = 10
    # Add code here to populate primary_friends
    count = 1
    try:
        for friends in tweepy.Cursor(api.friends, id=root_user).items():
            if count > no_of_friends:
                break
            else:
                try:
                    time.sleep(TIMER)
                    primary_friends.append(friends.screen_name)
                    count += 1
                except UnicodeEncodeError:
                    continue
    except tweepy.error.RateLimitError:
        # Wait for 15 minutes
        print "Error: Rate limit exceeded. Waiting for 15 minutes."
        time.sleep(900)

    return primary_friends

def getPrimaryFollowers(api, root_user, no_of_followers):
    # TODO: implement the method for fetching 'no_of_friends' primary friends of 'root_user'
    # rtype: list containing entries in the form of a tuple (root_user, friend)
    primary_followers = []
    TIMER = 10
    # Add code here to populate primary_friends
    count = 1
    try:
        for followers in tweepy.Cursor(api.followers, id=root_user).items():
            if count > no_of_followers:
                break
            else:
                try:
                    time.sleep(TIMER)
                    primary_followers.append(followers.screen_name)
                    count += 1
                except UnicodeEncodeError:
                    continue
    except tweepy.error.RateLimitError:
        # wait for 15 minutes
        print "Error: Rate limit exceeded. Waiting for 15 minutes."
        time.sleep(900)
    return primary_followers

# Q1.b.(ii) - 7 points
def getNextLevelFriends(api, friends_list, no_of_friends):
    # TODO: implement the method for fetching 'no_of_friends' friends for each entry in friends_list
    # rtype: list containing entries in the form of a tuple (friends_list[i], friend)
    next_level_friends = []
    for friend in friends_list:
        fl = getPrimaryFriends(api, friend, no_of_friends)
        for each in fl:
            next_level_friends.append((friend, each))
    return next_level_friends

# Q1.b.(iii) - 7 points
def getNextLevelFollowers(api, followers_list, no_of_followers):
    # TODO: implement the method for fetching 'no_of_followers' followers for each entry in followers_list
    # rtype: list containing entries in the form of a tuple (follower, followers_list[i])    
    next_level_followers = []
    # Add code here to populate next_level_followers
    for follower in followers_list:
        fl = getPrimaryFollowers(api, follower, no_of_followers)
        for each in fl:
            next_level_followers.append((follower, each))
    return next_level_followers

# Q1.b.(i),(ii),(iii) - 4 points
def GatherAllEdges(api, root_user, no_of_neighbours):
    # TODO:  implement this method for calling the methods getPrimaryFriends, getNextLevelFriends
    #        and getNextLevelFollowers. Use no_of_neighbours to specify the no_of_friends/no_of_followers parameter.
    #        NOT using the no_of_neighbours parameter may cause the autograder to FAIL.
    #        Accumulate the return values from all these methods.
    # rtype: list containing entries in the form of a tuple (Source, Target). Refer to the "Note(s)" in the 
    #        Question doc to know what Source node and Target node of an edge is in the case of Followers and Friends. 
    user = api.get_user(root_user)

    all_edges = [] 
    #Add code here to populate all_edges
    primary_friends = getPrimaryFriends(api, root_user, no_of_neighbours)
    next_level_friends = getNextLevelFriends(api, primary_friends, no_of_neighbours)
    next_level_followers = getNextLevelFollowers(api, primary_friends, no_of_neighbours)

    for prim_friend in primary_friends:
        all_edges.append((user.screen_name, prim_friend))
    for tuple in next_level_friends:
        all_edges.append(tuple)
    for tuple in next_level_followers:
        all_edges.append(tuple)

    return all_edges


# Q1.b.(i),(ii),(iii) - 5 Marks
def writeToFile(data, output_file):
    # write data to output_file
    # rtype: None
    # print data
    with open('graph.csv', 'w') as file:
        file.write("Source,Target\n")
        for each in data:
            file.write("{},{}\n".format(each[0], each[1]))






"""
NOTE ON GRADING:

We will import the above functions
and use testSubmission() as below
to automatically grade your code.

You may modify testSubmission()
for your testing purposes
but it will not be graded.

It is highly recommended that
you DO NOT put any code outside testSubmission()
as it will break the auto-grader.

Note that your code should work as expected
for any value of ROOT_USER.
"""

def testSubmission():
    KEY_FILE = 'keys.json'
    OUTPUT_FILE_GRAPH = 'graph.csv'
    NO_OF_NEIGHBOURS = 20
    ROOT_USER = 'PoloChau'

    api_key, api_secret, token, token_secret = loadKeys(KEY_FILE)

    auth = tweepy.OAuthHandler(api_key, api_secret)
    auth.set_access_token(token, token_secret)
    api = tweepy.API(auth)

    edges = GatherAllEdges(api, ROOT_USER, NO_OF_NEIGHBOURS)

    writeToFile(edges, OUTPUT_FILE_GRAPH)
    

if __name__ == '__main__':
    testSubmission()

