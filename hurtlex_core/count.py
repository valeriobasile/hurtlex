#!/usr/bin/env python


from searchtweets import ResultStream, gen_request_parameters, load_credentials
import os
import csv
from glob import glob
import sys
from time import sleep
from tqdm import tqdm

search_args = load_credentials(filename="./twitter_keys.yaml",
                 yaml_key="search_tweets_v2",
                 env_overwrite=False)
    
HURTLEX_DIR = "/home/basic/dev/hurtlex/lexica/"

with open("hurtlex_counts.csv.bak") as f:
    reader = csv.DictReader(f, fieldnames=["language", "id", "lemma", "count"])
    done = [row["id"] for row in reader]

fo = open("hurtlex_counts.csv", "w")
writer = csv.DictWriter(fo, fieldnames=["language", "id", "lemma", "count"])

for subdir in tqdm(glob(os.path.join(HURTLEX_DIR, "??"))):
    language = os.path.basename(subdir)
    with open (os.path.join(subdir, "1.2/hurtlex_{0}.tsv").format(language)) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            if row["id"] in done:
                continue           
            word = row["lemma"]
            filters = " lang:{0}".format(language.lower())
            query = gen_request_parameters(word+filters, results_per_call=10, granularity="day")
                   
            try:
                rs = ResultStream(request_parameters=query,
                                    tweetify=False,
                                    max_results=10000,
                                    max_pages=1,
                                    **search_args)
                count = 0            
                for tweet in rs.stream():
                    count += tweet["meta"]["total_tweet_count"]
                
                writer.writerow({
                    "language": language,
                    "id": row["id"],
                    "lemma": word, 
                    "count": count
                })
                sleep(2)
            except:
                print (language, word)

fo.close()
