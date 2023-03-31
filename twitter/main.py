from fileinput import filename
import pandas as pd
import tweepy
from TwitterAPI import TwitterAPI
import networkx as nx
import matplotlib.pyplot as plt
from csvtojson import convertToJSON
from plotgraphs import plotDegreeHistogram
import os 

#get the list of screen names mentioned in the tweet
def getMentionScreenname(array):
    res=[]
    if array:
        for x in array:
            res.append(x['screen_name'])
    return res

#developing a diffusion graph
#here the directed graph is being implemented 
#the direction are defined as : 
# if A mentions B in 'A' tweet: then A->B edge will be present
# if A retweets B's Tweet :  then A->B edge will be present 
def generateGraph(df):
    DG=nx.DiGraph()
    for _,row in df.iterrows():
        if row['user_mention']:
            for x in row['user_mention']:
                if x!=row['username'] and not DG.has_edge(row['username'],x):
                    DG.add_edge(row['username'],x)
        else:
            DG.add_node(row['username'])
        if row['retweetScreenNames'] != '' and row['retweetScreenNames']!=row['username']:
            DG.add_edge(row['username'],row['retweetScreenNames'])
    return DG
    
#scraping the tweets using query and twitter api object
def crawlTwitter(words, date_since,numtweet, api):
    cols=['username','created_at','truncated','description','following','followers','totaltweets','retweetcount','text','hashtags','user_mention','retweetScreenNames']
    db = pd.DataFrame(columns=cols)
    tweets = tweepy.Cursor(api.search_tweets,words, lang="en",since_id=date_since,tweet_mode='extended').items(numtweet)
    i = 1
    for x in tweets:
        screename = x.user.screen_name
        createdDate=x.created_at
        truncated=x.truncated
        description = x.user.description
        following = x.user.friends_count
        followers = x.user.followers_count
        totalTweets = x.user.statuses_count
        retweetCount = x.retweet_count
        hashTags = x.entities['hashtags']
        mention=x.entities['user_mentions']
        mention_screennames=getMentionScreenname(mention)
        retweetScreenNames=''
        try:
            text = x.retweeted_status.full_text
            retweetScreenNames=x.retweeted_status.user.screen_name
        except AttributeError:
            text = x.full_text
        ith_tweet = [screename,createdDate,truncated, description, following,followers, totalTweets,retweetCount, text, hashTags,mention_screennames,retweetScreenNames]
        db.loc[len(db)] = ith_tweet
        i = i + 1
    return db


#developing the query from list of keyword hashtags
def formQuery(tags):
    res=''
    for x in tags:
        res=res+x+' OR '
    res=res[:len(res)-4]
    return res

#creating the api object after authorisation using api key , access tokens
def getTweetAPI():

    api_key = '8RQ5xPiDzAg1duMVpj9pWYEdX'
    api_key_secret = 'BqfcElqH5G6yAFHafuMQWO5ljp8Bosa402DzldWgc3mzCOSrSB'
    access_token = '1570146620653850629-erndFgwUuLXuK8prEhhrpkqlBUICih'
    access_token_secret = 'hwjy8IzsfECPVje0SAzdg3YorFifjAZbpBBgmLxBxnGVc'

    
    auth = tweepy.OAuth1UserHandler(api_key, api_key_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)

#function to get the date from which scraping should be started in the twitter
def getSinceDate():
    print("FDA granted Covid vaccine from December,11 2020. Do you need tweets from the same date onwards (Y/N)")
    ans=input()
    date_since=''
    if ans.lower() =='y':
        date_since='2019-12-12'
    else:
        print("Enter the date from which tweets are required in yyyy-mm-dd")
        date_since = input()
    return date_since

#save the data into csv and json files
def saveIntoFiles(resultDataFrames):
    filenames=['proVaccineTweets','antiVaccineTweets']
    for x in range(len(resultDataFrames)):
        resultDataFrames[x].to_csv(filenames[x]+'.csv')
    for x in filenames:
        temp=os.path.join(os.getcwd(), x)
        convertToJSON(temp+'.csv',temp+'.json')
 
 #function responsibe for  api object creation and developing graph and plotting histograms.

def api_call(queries,numTweets):
    api=getTweetAPI()
    date_since=getSinceDate()
    resultDataframes=[]
    Graphs=[]
    for i in range(len(queries)):
        query=formQuery(queries[i])
        resultDataframes.append(crawlTwitter(query, date_since,numTweets, api))
    for x in resultDataframes:
        Graphs.append(generateGraph(x))
    saveIntoFiles(resultDataframes)
    plotDegreeHistogram(Graphs)
    fig = plt.figure(1, figsize=(100, 80), dpi=40)
    nx.draw_networkx(Graphs[0],node_size=2000,node_color='b',edge_color='g',width=1,font_size=5)
    plt.title('Directed Graph for Pro Vaccine')
    plt.show()
    plt.clf()
    fig = plt.figure(1, figsize=(1000, 800), dpi=40)
    nx.draw_networkx(Graphs[1],node_size=1000,node_color='b',edge_color='g',width= 1,font_size=5)
    plt.title('Directed Graph for Anti Vaccine')
    plt.show()
    print('Done!')

    

if __name__ == '__main__':
    proVaccine=['#GetVaccinated','#VaccineMandate','#VaccinesWork','#FullyVaccinated','GetVaccinatedOrGetCovid']
    antiVaccine=['#vaccineinjury','#NoVaccineMandates','#SayNoToVaccineMandate','#NoVaxMandates','#AntiVaccine']
    queries=[proVaccine,antiVaccine]
    numTweets=300
    api_call(queries,numTweets)
