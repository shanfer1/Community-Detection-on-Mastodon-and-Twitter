# -*- coding: utf-8 -*-
"""MastodonDataCollection.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1HEr8z3-2Jgwiw6QvR-VMXNuSf7aqsy1n
"""

#get the data 

import pandas as pd
import requests # to fetch data 
import re # to use regular expressions on strings
import pandas as pd # to show final results in a table
import re

#the data coming from the drive is : id , uri, url ,content , account[username], account['id']
columns = ['user_id', 'username','content','url','uri']

# Create an empty DataFrame with the defined column names
df = pd.DataFrame(columns=columns)

#prepare hashtags:


filename = 'hashtags.txt'  # Replace with your desired filename
hashtags = []  # Initialize an empty list to store the lines

# Open the file and read its contents line by line
with open(filename, 'r',encoding='utf-8') as f:
    for line in f.readlines():
        # Strip whitespace from the line and split it into a list of words
        words = line.strip().split()
        
        # Join the words in the list with commas and append the resulting string to the list
        hashtags.append(''.join(words))

# Print the resulting list
print(hashtags)



# hashtags=['NoVaccine','NoVaccineMandates','SayNoToVaccineMandate','NoVaxMandates','FuckTheVax','FuckVaccines','AntiVaccine','NoForcedVaccines','GetVaccinated','GetVaxxed','VaxPlus','VaccineMandate','GetVaccinatedNow','MandatoryVaccination','VaccinesWork','VaccinationWork','FullyVaccinated','VaccinesSaveLives','VaccinatedForCovid','AntivacinIdiots','ProScience']
print(len(hashtags))

hashtags[0] = hashtags[0].lstrip('\ufeff')[:]
hashtags=hashtags[:10]+ hashtags[25:35]
print(len(hashtags))
print(hashtags)

import pandas as pd
# Create an empty DataFrame with the defined column names
df_new = pd.DataFrame(columns=['user_id', 'username', 'content', 'hashtag', 'url', 'uri', 'reblogged_user_id'])

import requests
import time
import re
import datetime
from dateutil.parser import parse

api_base_url = 'https://mastodon.social/api/v1/'

# Initialize variables for rate limiting
remaining_requests = 0
reset_time_remaining = 0
i=0
for hashtag in hashtags:
    print(f'the hashtags number is {i}')
    i+=1
    limit = 80  # Set the maximum number of statuses to retrieve per page
    max_id = None  # Initialize the max_id parameter to None
    
    # Loop through the pages of statuses until all statuses have been retrieved
    while True:
        # Construct the API URL to retrieve the statuses for the hashtag
        url = api_base_url + f'timelines/tag/{hashtag}?limit={limit}'
        if max_id is not None:
            url += f"&max_id={max_id}"
        
        # Make the API call to retrieve the statuses
        response = requests.get(url)
        
        # Handle rate limiting
        if response.status_code == 429:  # Too Many Requests
            remaining_requests = int(response.headers.get('X-Ratelimit-Remaining', 0))
            reset_time_str = response.headers.get('X-Ratelimit-Reset', None)
            if reset_time_str:
                reset_time = parse(reset_time_str)
                reset_time_remaining = int((reset_time - datetime.datetime.now(datetime.timezone.utc)).total_seconds())
            else:
                reset_time_remaining = 0

            print(f"Rate limit reached. Sleeping for {reset_time_remaining} seconds.")
            time.sleep(reset_time_remaining)
            continue  # Retry the API call after sleeping

        # Retrieve the statuses from the API response
        if response.status_code == 200:
            statuses = response.json()
            if len(statuses) == 0:
                # No more statuses to retrieve
                break
            else:
                # Iterate over the retrieved statuses and store the relevant data in the dataframe
                for status in statuses:
                    user_id = status['account']['id']
                    username = status['account']['username']
                    content = status['content']
                    url = status['url']
                    uri = status['uri']
                    
                    # Make the API call to retrieve the reblogs for the status
                    reblog_url = api_base_url + f'statuses/{status["id"]}/reblogged_by'
                    
                    # Handle rate limiting
                    # if remaining_requests <= 1 and reset_time_remaining > 0:
                    #     print(f"Rate limit reached. Sleeping for {reset_time_remaining} seconds.")
                    #     time.sleep(reset_time_remaining)

                    reblog_response = requests.get(reblog_url)
                    
                    # Handle rate limiting
                    if reblog_response.status_code == 429:  # Too Many Requests
                        remaining_requests = int(reblog_response.headers.get('X-Ratelimit-Remaining', 0))
                        reset_time_str = reblog_response.headers.get('X-Ratelimit-Reset', None)
                        if reset_time_str:
                            reset_time = parse(reset_time_str)
                            reset_time_remaining = int((reset_time - datetime.datetime.now(datetime.timezone.utc)).total_seconds())
                        else:
                            reset_time_remaining = 0

                        print(f"Rate limit reached. Sleeping for {reset_time_remaining} seconds.")
                        time.sleep(reset_time_remaining)
                        continue  # Retry the API call after sleeping

                    # Retrieve the reblog data from the API response
                    if reblog_response.status_code == 200:
                        reblogs = reblog_response.json()
                        reblogged_user_ids = [reblog['id'] for reblog in reblogs]
                    else:
                        reblogged_user_ids = []

                    # Append the retrieved data to the dataframe
                    df_new.loc[len(df_new.index)] = [user_id, username,content,hashtag,url,uri,reblogged_user_ids]
                
                    # Update the max_id parameter for the next page
                    max_id = status['id']
        
        else:
            print(f"API call failed with status code {response.status_code}")
            break
        
print("Total data length:", len(df_new))




df_new.to_csv("final_data_with_rebolg_unclean.csv")

import re



# Define a function to remove HTML tags
def remove_tags(text):
    clean_text = re.sub('<.*?>', '', text)
    return clean_text

# Apply the function to each row of the DataFrame
df_new['clean_text'] = df_new['content'].apply(remove_tags)

# Print the result
print(df_new['clean_text'])

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from nltk.chunk import ne_chunk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')

# Load data from Pandas dataframe

# Tokenization
df_new['tokens'] = df_new['clean_text'].apply(word_tokenize)

# Stopword removal
stop_words = set(stopwords.words('english'))
df_new['tokens'] = df_new['tokens'].apply(lambda x: [word for word in x if word.lower() not in stop_words])

# Stemming or lemmatization
lemmatizer = WordNetLemmatizer()
df_new['tokens'] = df_new['tokens'].apply(lambda x: [lemmatizer.lemmatize(word) for word in x])

# Part-of-speech tagging
df_new['pos_tags'] = df_new['tokens'].apply(pos_tag)

# Named entity recognition
df_new['ner_tags'] = df_new['pos_tags'].apply(ne_chunk)

# Co-occurrence matrix
vectorizer = CountVectorizer(tokenizer=lambda doc: doc, lowercase=False)
matrix = vectorizer.fit_transform(df_new['tokens'].apply(lambda x: " ".join(x)))
cooccurrence_matrix = (matrix.T * matrix)

# TF-IDF weighting
tfidf_vectorizer = TfidfVectorizer(tokenizer=lambda doc: doc, lowercase=False)
tfidf_matrix = tfidf_vectorizer.fit_transform(df_new['tokens'].apply(lambda x: " ".join(x)))

df_new.to_csv("final_data_with_rebolg.csv")
print("done")

