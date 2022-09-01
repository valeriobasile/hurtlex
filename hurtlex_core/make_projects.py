#!/usr/bin/env python

import pandas as pd
import os
from glob import glob
import csv
from tqdm import tqdm

HURTLEX_DIR = "/home/basic/dev/hurtlex/lexica/"

posmap = {
"n" : "noun",
"a" : "adjective",
"av" : "adverb",
"v" : "verb"
}

df = pd.read_csv("hurtlex_counts.csv", names=["language", "id", "lemma", "c"])

for subdir in tqdm(glob(os.path.join(HURTLEX_DIR, "??"))):
    language = os.path.basename(subdir)    
    
    # read POS
    pos = dict()
    with open ("{0}{1}/1.2/hurtlex_{1}.tsv".format(HURTLEX_DIR, language)) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            pos[row["id"]] = row["pos"]
    
    dfl = df[(df.language==language) & (df.c > 0)].sort_values(by='c', ascending=False)
    dfl = dfl.iloc[:,1:3].drop_duplicates().head(501)
    if dfl.empty:
        continue
    
    with open(os.path.join("projects", "hurtlexcore_{0}.tsv".format(language)), "w") as fo:
        writer = csv.DictWriter(fo, delimiter="\t", fieldnames = ["id", "lemma"])
        dfl = dfl.sample(frac = 1)
        for row in dfl.itertuples():
            writer.writerow({"id": row[1], "lemma":  "{0} ({1})".format(row[2], posmap[pos[row[1]]])})
