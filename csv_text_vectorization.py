#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 15:54:17 2020

@author: drewcolbert
"""


from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import re
'''
This module takes raw movie reviews and restaurant reviews that include labels
(pos or neg) and reads in the csv files, seperates the labels from the raw text,
uses CountVectorizer and TfidfVectorizer to create a sparse matrix of word counts 
from each review. The matrices are then converted to pandas data frames and the labels 
are added on to the data frame
'''
#####################################################################################
#           RESTAURANT DATA                                                         #
#####################################################################################

# CREATE AN EMPTY LIST FOR THE LABELS AND THE REVIEW TEXT TO GO INTO
label_list = []
review_list = []

# OPEN THE CSV FILE
with open("RestaurantData.csv", "r") as rest_file:
    # WE DONT WANT TO READ THE FIRST LINE, SO WE "READ" IT AND THEN DO NOTHING
    rest_file.readline()
    # FOR THE REST OF THE LINES: 
    # SPLIT THE LABEL AND THE REVIEW
    # THIS IS EASY BECASUE WHEN WE LOOK AT THE RAW FILE, THE LABEL IS
    # BEFORE THE REST OF THE REVIEW AND WE KNOW THE TEXT IS SEPERATED BY COMMAS
    for row in rest_file:
        # ONLY SPLIT ONCE SO WE HAVE LABEL AND REVIEW
        # ADD THESE INTO THE LISTS CREATED BEFORE
        label, review = row.split(",", 1)
        label_list.append(label)
        review_list.append(review)

# CREATE BOTH OF THE VECTORIZERS, AND FIT THE DATA TO THEM
c_vector = CountVectorizer(input = "content",
                          stop_words = "english",
                          lowercase = True)

tf_vector = TfidfVectorizer(input = "content",
                            stop_words = "english",
                            lowercase = True)

text_dataC = c_vector.fit_transform(review_list)
text_dataTF = tf_vector.fit_transform(review_list)

column_names = c_vector.get_feature_names()

# CREATE THE DATAFRAMES WITH EACH WORD AS THE COLUMNS
text_dfC = pd.DataFrame(text_dataC.toarray(), columns = column_names)
text_dfTF = pd.DataFrame(text_dataTF.toarray(), columns = column_names)

# IS THE COLUMN HAS A NUMBER IN IT, WE DROP IT
for column in text_dfC.columns:
    if re.search("\d", column):
        text_dfC.drop(column, axis = 1, inplace = True)

for column in text_dfTF.columns:
    if re.search("\d", column):
        text_dfTF.drop(column, axis = 1, inplace = True)
        
# ADD THE LABELS TO EACH DF
text_dfC["LABELS"] = label_list
text_dfTF["LABELS"] = label_list

#####################################################################################
#           MOVIE DATA                                                              #
#####################################################################################
'''
MOVIE DATA IS MORE COMPLICATED BECAUSE THE LABEL IS NOT SO NICLEY SEPERATED FROM 
THE REST OF THE DATA. THE LABEL IS LOCATED AT THE END OF THE DATA SO MORE STEPS
ARE REQUIRED TO GET IT
'''

# START WITH AN EMPTY LIST TO PUT THE DATA INTO
raw_text_listed = []
with open("MovieData.csv", "r") as movie_file:
    # READ THE FIRST LINE AND IGNORE IT BECAUSE WE DONT NEED IT
    movie_file.readline()
    for row in movie_file:
        # STRIP THE WHITESPACE FROM THE ROWS
        row = row.rstrip(" ")
        # SPLIT BY COMMAS 
        # THERE IS GOING TO BE A LOT OF SPLITS, DEPENDING ON HOW MANY 
        # COMMAS WERE USED 
        split_text = row.split(",")
        raw_text_listed.append(split_text)
        
#  THE LIST HAD A BUNCH OF ELEMENTS THAT WERE EMPTY 
# GET RID OF ALL THE EMPTY ELEMENTS 
for i in range(len(raw_text_listed)):
    raw_text_listed[i] = list(filter(None, raw_text_listed[i]))

# DELETE LEFTOVER EMPTY ELEMENTS
# NOT SURE WHY THERE WAS LEFTOVERS IN THESE TWO REVIEWS ??????
del raw_text_listed[2][29]
del raw_text_listed[3][47]

# STRIPPING THE LABELS FROM EACH REVIEW     
labels = []
for review in raw_text_listed:
    # REVERSE THE ORDER OF THE LIST SO THE LABEL IS THE FIRST ELEMENT
    review_flipped = review[::-1]
    # CAPTURE THE LABEL AND APPEND IT TO THE LIST
    movie_label = review_flipped[0]
    labels.append(movie_label)
    # DELETE THE LABEL FROM THE ORIGINAL REVIEW
    last_index = len(review) - 1
    del review[last_index]

# COUNT VECTORIZER CANNOT TAKE IN A LIST OF LISTS WHICH IS WHAT WE CURRENTLY HAVE
# WE NEED TO UNLIST EACH REVIEW AND MAKE IT ONE STRING
raw_text_unlisted = []
# JOINING A LIST OF STRINGS TO ANOTHER EMPTY STRING
# APPENDING THIS NEW STRING TO ANOTHER LIST
raw_text_unlisted.append("".join(raw_text_listed[0]))
raw_text_unlisted.append("".join(raw_text_listed[1]))
raw_text_unlisted.append("".join(raw_text_listed[2]))
raw_text_unlisted.append("".join(raw_text_listed[3]))
raw_text_unlisted.append("".join(raw_text_listed[4]))   
                       

# CREATE BOTH OF THE VECTORIZERS, AND FIT THE DATA TO THEM
c_vector2 = CountVectorizer(input = "content",
                            stop_words = "english")

tf_vector2 = TfidfVectorizer(input = "content",
                             stop_words = "english")

movie_dataC = c_vector2.fit_transform(raw_text_unlisted)
movie_dataTF = tf_vector2.fit_transform(raw_text_unlisted)

movie_columns = c_vector2.get_feature_names()

# CREATE THE DATAFRAMES WITH EACH WORD AS THE COLUMNS
movie_text_dfC = pd.DataFrame(movie_dataC.toarray(), columns = movie_columns)
movie_text_dfTF = pd.DataFrame(movie_dataTF.toarray(), columns = movie_columns)

# IS THE COLUMN HAS A NUMBER IN IT, WE DROP IT
for column in movie_text_dfC.columns:
    if re.search("\d", column) or len(column) <= 3:
        movie_text_dfC.drop(column, axis = 1, inplace = True)

for column in movie_text_dfTF.columns:
    if re.search("\d", column) or len(column) <=3:
        movie_text_dfTF.drop(column, axis = 1, inplace = True)

# ADD THE LABELS TO EACH DF
movie_text_dfC["LABELS"] = labels
movie_text_dfTF["LABELS"] = labels





        
    




























