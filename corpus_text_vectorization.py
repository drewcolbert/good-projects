#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 14:25:25 2020

@author: drewcolbert
"""


from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import os


# THIS IS THE PATH WHERE THE CORPUS FOLDERS ARE LOCATED
original_path = "/Users/drewcolbert/Documents/Programs/Blakes_Pizza_Corpus/"

# MAKE SURE WE CAN GET ALL THE FILES IN THE POSITIVE AND NEGATIVE FOLDERS
pos_files = os.listdir(original_path + "POS")
#print(pos_files)
neg_files = os.listdir(original_path + "NEG")
#print(neg_files)


complete_paths = []
labels = []
# GET THE PATHS TO THE TWO FOLDERS
for name in ["POS", "NEG"]:
    files = os.listdir(original_path + name)
    
    # GET THE FINAL PATHS TO EACH FILE IN EACH CORPUS
    for file in files:
        full_path = original_path + str(name) + "/" + str(file)
        complete_paths.append(full_path)
        labels.append(name)

# CREATE THE CV TO TOKENIZE AND VECTORIZE EACH DOCUMENT 
CV2 = CountVectorizer(input = "filename", 
                      stop_words = "english", 
                      lowercase = True,
                      decode_error = "ignore")

# FIT THE CV TO THE PATHS WE JUST CREATED 
text_data = CV2.fit_transform(complete_paths)

# THESE WILL BE THE COLUMN NAMES
vocab = CV2.get_feature_names()

# CREATE THE DATAFRAME WITH THE WORDS AS THE COLUMNS 
# THE WORD FREQUENCIES FILL IN THE CELLS IN THE DATAFRAME
# THE DTM MUST BE CONVERTED TO AN ARRAY BEFORE BEING TRANSFORMED TO A DF
text_df = pd.DataFrame(text_data.toarray(), columns = vocab)

# ADD THE KNOWN LABELS TO THE DATAFRAME
# GOTTEN FROM THE FOLDER NAMES OF EACH CORPUS WHERE THE FILE WAS LOCATED
text_df["Labels"] = labels
        
    
    





















