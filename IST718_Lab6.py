#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 31 20:11:50 2020

@author: drewcolbert
"""


import pandas as pd
import matplotlib as plt
import seaborn as sns
from functools import reduce

# READ IN THE DATA
full_housing_data = pd.read_csv("housing_data.csv")

# USE THE FIRST 20 ROWS TO GET THE CODE RIGHT 
mess_around = full_housing_data.head(20)

# SEE WHAT COLUMNS WE HAVE.... TIME SERIES!!!!
# WHAT DOES THE DATA UNDER THE DATES REPRESENT THOUGH.... MEDIAN HOUSING VALUE!!
columns = full_housing_data.columns


################################################################################
#      CREATING TIME SERIES CHART FOR 4 DIFFERENT METRO AREAS IN ARKANSAS      #
################################################################################

# EXTRACT ALL OF THE DIFFERENT CITIES FROM OUR FULL DATA SET
little_rock = full_housing_data.loc[lambda df: df['City'] == "Little Rock"]
hot_springs = full_housing_data.loc[lambda df: df['City'] == "Hot Springs"]
fayette = full_housing_data.loc[lambda df: df['City'] == "Fayetteville"]
searcy = full_housing_data.loc[lambda df: df['City'] == "Searcy"]

# MERGE ALL OF THE DATAFRAMES INTO ONE
# USE OUTER JOIN SO NONE OF THE DATA GETS LOST
all_df = [little_rock, hot_springs, fayette, searcy]
arkansas = reduce(lambda left, right: pd.merge(left, right, how = "outer"), all_df)
# ONLY WANT THE CITIES LOCATED IN ARKANSAS
arkansas = arkansas.loc[arkansas["State"] == "AR"]

'''
At this point, we have extracted all of the 4 different target cities in arkansas 
and put them into one dataframe. All of the different dates are located as columns
at this point. We want to go from a wide dataframe to a long dataframe. Using the 
melt function, we can take the columns and melt them into one. The id_vars are the
columns that we don't want to alter and the remaining columns will get melted into 
one with the values put into another column
'''
arkansas_melted = arkansas.melt(id_vars = ["RegionID", 
                                           "SizeRank", 
                                           "RegionName", 
                                           "RegionType", 
                                           "StateName", 
                                           "State",
                                           "City",
                                           "Metro",
                                           "CountyName"],
                                var_name = "Date",
                                value_name = "MedianHousingValue")

# CHANGE THE DATE COLUMN TO TYPE DATETIME
arkansas_melted["Date"] = pd.to_datetime(arkansas_melted["Date"], 
                                         infer_datetime_format = True)

# GROUP BY THE METRO (4 DIFFERENT METROS) TO GET AN IDEA OF THE DIFFERENCES
arkansas_grouped = arkansas_melted.groupby(["Metro"]).mean()  

# CHART THE AVERAGE MEDIAN HOUSING VALUES FOR EACH METRO OVER TIME
sns.lineplot(x = "Date",
            y = "MedianHousingValue",
            data = arkansas_melted,
            hue = "Metro",
            ci = None)































            
                       
                                                    


