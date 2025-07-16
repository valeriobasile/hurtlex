#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from glob import glob
import pandas as pd

for filename in glob('*/*.csv'):
    lang = filename.split('/')[-2]
    print (filename, lang)
    #df = pd.read_csv(filename, index_col=0)