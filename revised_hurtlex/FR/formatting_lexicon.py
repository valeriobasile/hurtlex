#!/usr/bin/env python
# coding: utf-8

# In[18]:


#!pip install pandas nltk
#!pip install toml
#!pip install wn
get_ipython().system('pip install spacy')
get_ipython().system('python -m spacy download fr_core_news_sm')


# In[16]:


### GET LEMMAS
import pandas as pd
import spacy

# Load the French language model in spaCy
nlp = spacy.load("fr_core_news_sm")

# Function to lemmatize a given text using spaCy
def lemmatize_text(text):
    doc = nlp(text)
    return ' '.join([token.lemma_ for token in doc])

# Load the TSV file
file_path = 'hurtlex_core/projects/hurtlexcore_FR.tsv'  # Replace with your actual file path
df = pd.read_csv(file_path, delimiter='\t', header=None)

# Assuming the second column is unnamed, you can reference it by index
second_column_name = df.columns[1]

# Create a new column with the lemmas
df['Lemma'] = df[second_column_name].apply(lemmatize_text)

# Save the updated DataFrame to a new CSV file
output_file_path = 'output_with_lemmas.csv'  # Replace with desired output file path
df.to_csv(output_file_path, index=False)

print(f"Processed file saved as {output_file_path}")


# In[19]:


### REMOVE DUPLICATE

import pandas as pd

# Load the CSV file
file_path = 'output_with_lemmas.csv'  # Replace with your actual file path
df = pd.read_csv(file_path)

# Remove duplicates based on the fourth column (index 3)
df_unique = df.drop_duplicates(subset=df.columns[3])

# Save the unique data to a new CSV file
output_file_path = 'output_deduplicate.csv'  # Replace with desired output file path
df_unique.to_csv(output_file_path, index=False, encoding='utf-8')

print(f"Processed file saved as {output_file_path}")


# In[20]:


import pandas as pd

# Load the first TSV file (no header, tab-delimited)
first_file_path = 'output_deduplicate.csv'  # Replace with your actual first file path
df1 = pd.read_csv(first_file_path)

# Load the second TSV file (no header, tab-delimited)
second_file_path = 'hurtlex_core/projects/wn-data-fra.tab'  # Replace with your actual second file path
df2 = pd.read_csv(second_file_path, delimiter='\t', header=None)
print(df2.iloc[:, 2])

# Create a dictionary from the second file to map third column values to the first column values
mapping_dict = dict(zip(df2.iloc[:, 2], df2.iloc[:, 0]))
print(df1.iloc[:, 0])

# Create a new column 'own-id' in the first dataframe by mapping the second column
df1['own-id'] = df1.iloc[:, 0].map(mapping_dict)

# Save the updated DataFrame to a new TSV file
output_file_path = 'output_with_own_id.tsv'  # Replace with desired output file path
df1.to_csv(output_file_path, sep='\t', index=False, header=False)

print(f"Processed file saved as {output_file_path}")


# In[4]:


import urllib.request
import urllib.parse
import json
import gzip
import pandas as pd
from io import BytesIO

# BabelNet API service URL
service_url = 'https://babelnet.io/v9/getSynsetIds'
#service_url = 'https://babelnet.io/v9/getSynset'

# BabelNet API key
key = 'YOUR KEY'  # Replace with your actual BabelNet API key

# Function to query the BabelNet API
def query_babelnet(lemma, lang='FR'):
    params = {
        'lemma': lemma,
        'searchLang': lang,
        'key': key
        # 'id' : lemma,
        # 'key'  : key,
        # 'targetLang' : lang

    }
    url = service_url + '?' + urllib.parse.urlencode(params)
    request = urllib.request.Request(url)
    request.add_header('Accept-encoding', 'gzip')
    
    try:
        with urllib.request.urlopen(request) as response:
            if response.info().get('Content-Encoding') == 'gzip':
                buf = BytesIO(response.read())
                f = gzip.GzipFile(fileobj=buf)
                data = json.loads(f.read())
                if data:  # Check if the data list is not empty
                    return data[0]['id']  # Return the first BabelNet ID
    except Exception as e:
        print(f"Error querying BabelNet for lemma '{lemma}': {e}")
    return None

# Load the CSV file
# file_path = 'hurtlex_core/projects/hurtlexcore_FR.tsv'  # Replace with your actual file path
file_path = 'output_with_own_id.tsv'
df = pd.read_csv(file_path, delimiter='\t', header=None)

# # Add a new column 'bn-id' with the BabelNet IDs
df['bn-id'] = df.iloc[:, 0].apply(query_babelnet)

# Save the updated DataFrame to a new CSV file
output_file_path = 'output_with_bn_id.csv'  # Replace with desired output file path
df.to_csv(output_file_path, index=False)

print(f"Processed file saved as {output_file_path}")


# In[23]:


### GET ALL SYNSET IDS FOR A GIVEN LIST OF LEMMA

import urllib.request
import urllib.parse
import json
import gzip
import pandas as pd
from io import BytesIO

# BabelNet API service URL
service_url = 'https://babelnet.io/v9/getSynsetIds'
key = 'YOUR KEY'  # Replace with your actual BabelNet API key

# Function to join with underscore if there's a space
def join_babelnet_id(word):
    return '_'.join(word.split()) if ' ' in word else word

# Function to query BabelNet API using an ID and target language
def query_babelnet_synset(lemma, target_lang='FR'):
    params = {
        'lemma': join_babelnet_id(lemma),
        'searchLang': target_lang,
        'key': key
    }
    url = service_url + '?' + urllib.parse.urlencode(params)
    print(f"Querying URL: {url}")
    request = urllib.request.Request(url)
    request.add_header('Accept-encoding', 'gzip')

    try:
        with urllib.request.urlopen(request) as response:
            if response.info().get('Content-Encoding') == 'gzip':
                buf = BytesIO(response.read())
                f = gzip.GzipFile(fileobj=buf)
                data = json.loads(f.read())
                return data
    except Exception as e:
        print(f"Error querying BabelNet for lemma '{lemma}': {e}")
        return None

# Load the CSV file
file_path = 'output_with_bn_id.csv'  # Replace with your actual file path
df = pd.read_csv(file_path)

# Dictionary to hold the final data to be written to a JSON file
output_data = []

# Process each row in the CSV file
for index, row in df.iterrows():
    lemma = row['lemma']  # Assuming the lemma is in a column named 'lemma'
    babelnet_data = query_babelnet_synset(lemma)
    
    if babelnet_data:
        for entry in babelnet_data:
            entry['lemma'] = lemma  # Add the lemma to each entry
            output_data.append(entry)

# Save the collected data to a JSON file
output_file_path = 'babelnetSynset_data.json'  # Replace with desired output file path
with open(output_file_path, 'w') as json_file:
    json.dump(output_data, json_file, indent=4)

print(f"Processed data saved as {output_file_path}")


# In[1]:


### GET SYNSET

import urllib.request
import urllib.parse
import json
import gzip
from io import BytesIO

# BabelNet API service URL
service_url = 'https://babelnet.io/v9/getSynset'
key = 'YOUR KEY'  # Replace with your actual BabelNet API key

# Function to join with underscore if there's a space
def join_babelnet_id(word):
    return '_'.join(word.split()) if ' ' in word else word

# Function to query BabelNet API using an ID and target language
def query_babelnet_synset(babelnet_id, lemma, target_lang='FR'):
    params = {
        'id': babelnet_id,
        'orig': join_babelnet_id(lemma),
        'lang': target_lang,
        'key': key
    }
    url = service_url + '?' + urllib.parse.urlencode(params)
    print(f"Querying URL: {url}")
    request = urllib.request.Request(url)
    request.add_header('Accept-encoding', 'gzip')

    try:
        with urllib.request.urlopen(request) as response:
            if response.info().get('Content-Encoding') == 'gzip':
                buf = BytesIO(response.read())
                f = gzip.GzipFile(fileobj=buf)
                data = json.loads(f.read())
                return data
    except Exception as e:
        print(f"Error querying BabelNet for ID '{babelnet_id}': {e}")
        return None

# Load the JSON file
file_path = 'babelnetSynset_data.json'  # Replace with your actual file path
with open(file_path, 'r') as json_file:
    json_data = json.load(json_file)

# List to hold the final data to be written to a JSON file
output_data = []

#Process each entry in the JSON file
for entry in json_data:
    babelnet_id = entry['id']  # Extract the BabelNet ID
    lemma = entry['lemma']  # Extract the lemma
    synset_data = query_babelnet_synset(babelnet_id, lemma)
    
    if synset_data:
        # Add the synset data to the output along with the original lemma and ID
        output_data.append({
            'babelnet_id': babelnet_id,
            'lemma': lemma,
            'synset_data': synset_data
        })

# Save the collected data to a JSON file
output_file_path = 'babelnetSenses_data.json'  # Replace with desired output file path
with open(output_file_path, 'w') as json_file:
    json.dump(output_data, json_file, indent=4)

print(f"Processed data saved as {output_file_path}")


# In[6]:


import json
import csv

# Specify the input JSON file and output CSV file
input_json_file = 'babelnetSenses_data.json'  # Replace with your input file path
output_csv_file = 'FR_HURNET.csv'  # Replace with your desired output file path

# Load the JSON data from the file
with open(input_json_file, 'r') as f:
    data = json.load(f)

# Initialize a list to store results
result = []

# Iterate over each item in the list
for item in data:
    # Extract the babelnet_id and lemma
    babelnet_id = item["babelnet_id"]
    lemma = item["lemma"]

    # Aggregate examples, glosses, and categories
    aggregated_examples = set()  # Use a set to avoid duplicates
    aggregated_glosses = set()  # Use a set to avoid duplicates
    aggregated_categories = set()  # Use a set to avoid duplicates

    # Iterate through each sense in the synset_data
    for sense in item["synset_data"]["senses"]:
        # Check if the source is either WN or OEWN
        source = sense["properties"]["source"]
        if source == "WN" or source == "OEWN":
            # Extract the lemma and pos
            sense_lemma = sense["properties"]["lemma"]["lemma"]
            pos = sense["properties"]["pos"]
            # Add the extracted data to the result list
            result.append({
                "babelnet_id": babelnet_id,
                "lemma": lemma,
                "sense_lemma": sense_lemma,
                "pos": pos,
                "examples": "",  # Placeholder, will be updated later
                "glosses": "",   # Placeholder, will be updated later
                "categories": ""  # Placeholder, will be updated later
            })

    # Iterate through the examples to aggregate them
    for example in item["synset_data"]["examples"]:
        if example["source"] == "WN" or example["source"] == "OEWN":
            aggregated_examples.add(example["example"])  # Add to set

    # Iterate through the glosses to aggregate them
    for gloss in item["synset_data"]["glosses"]:
        if gloss["source"] == "WN" or gloss["source"] == "OEWN":
            aggregated_glosses.add(gloss["gloss"])  # Add to set

    # Aggregate categories
    if "synsetType" in item["synset_data"] and item["synset_data"]["synsetType"] == "CONCEPT":
        if "categories" in item["synset_data"]:
            for category in item["synset_data"]["categories"]:
                if category["language"] == "EN":  # Filter by language if necessary
                    aggregated_categories.add(category["category"])  # Add to set

    # Update the examples, glosses, and categories in the results
    for entry in result:
        if entry["babelnet_id"] == babelnet_id and entry["lemma"] == lemma:
            entry["examples"] = " | ".join(sorted(aggregated_examples))  # Sort for consistent ordering
            entry["glosses"] = " | ".join(sorted(aggregated_glosses))  # Sort for consistent ordering
            entry["categories"] = " | ".join(sorted(aggregated_categories))  # Sort for consistent ordering

# Remove duplicate rows from the result list
unique_results = []
seen = set()

for entry in result:
    # Create a tuple from the entry values to use as a set key
    entry_tuple = (
        entry["babelnet_id"], entry["lemma"], entry["sense_lemma"], entry["pos"], 
        entry["examples"], entry["glosses"], entry["categories"]
    )
    if entry_tuple not in seen:
        seen.add(entry_tuple)
        unique_results.append(entry)

# Write the unique results to a CSV file
with open(output_csv_file, 'w', newline='') as csvfile:
    fieldnames = ['babelnet_id', 'lemma', 'sense_lemma', 'pos', 'examples', 'glosses', 'categories']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for entry in unique_results:
        writer.writerow(entry)

print(f"Data has been written to {output_csv_file}")


# In[ ]:




