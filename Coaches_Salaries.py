#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 14:02:34 2020

@author: drewcolbert
"""


from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
import pandas as pd
from functools import reduce
import seaborn as sns
import matplotlib as plt
import numpy as np
import statsmodels.formula.api as smf

''' This modules goal is to create a linear model to predict the salary of 
a head football coach of a division 1 program. There is 6 different parts.
1. Download the original data into python (salaries_data)
2. Use beautiful soup to scrape the web for more information to go into
the model. (Revenue Data, record data)
        There was a problem with stadium data that I could not figure out
        in time
3. merge all of the dataframes together to get a final dataset for EDA
and model creation (99 rows, 9 columns)
4. Perform EDA and create charts. Looked at revenue of team vs the coaches 
salary, wins vs salary, revenue per conference, salary per conference
5. Create the linear model. The conferences came out with p-values above .05,
they were kept in the model because of discoveries made by the EDA
6. Create a function that allows a user to input 4 variables and returns
the suggested salary based on the data collected previously '''


#####################################################################################
#       READ IN CSV FILES COLLECTED                                           #
#####################################################################################

# READ IN A CSV CONTAINING COACHES SALRY DATA FOR EACH TEAM 
salary_data = pd.read_csv("Coaches9.csv")
# DROP ASSISTANTPAY AS A COLUMN (ALL VALUES WERE 0)
salary_data.drop("AssistantPay", 1, inplace = True)

# READ IN A CSV CONTAINING REVENUES FOR EACH TEAM
revenue_data = pd.read_csv("IST718_Lab1_Revenues.csv")
revenue_data = revenue_data.drop(["Confrence"], axis = 1)

'''
#####################################################################################
#       COLLECTING STADIUM DATA FOR EACH TEAM                                       #
#####################################################################################

# SEND A REQUEST TO THE WEBISTE TO BEGIN PARSING 
my_url = "https://en.wikipedia.org/wiki/List_of_NCAA_Division_I_FBS_football_stadiums"
uClient = urlopen(my_url)
page_html = uClient.read()
uClient.close()

# CREATE A PARSER TO READ THROUGH THE HTML
page_soup = soup(page_html, "html.parser")

#containers = page_soup.findAll("tr", limit = 132)
# FIND THE TAGS THAT CONTAIN THE DATA FOR EACH CELL 
cells = page_soup.findAll("td", limit = 1452)
# EMPTY DICTIONARY FOR STADIUM DATA TO BE PUT INTO
stadium_data = {}

# INDEX 1 IS THE FIRST 121 STADIUMS IN THE TABLE
# INDEX 2 IS THE LAST 9 STADIUMS IN THE TABLE
index_list1 = list(range(1,1331))
index_list2 = list(range(1331, 1420))
# WE ONLY WANT THE TEXT FROM EVERY 11 TAGS 
# (EACH STADIUM IS 11 SPACES AWAY IN THE TABLE)
# (THIS IS THE CASE FOR ALL OF THE DATA BEING COLLECTED)
stadium_index1 = index_list1[0::11]
stadium_index2 = index_list2[0::11]
# GET THE TEXT FROM EACH TAG CONTAINING THE STADIUM NAME
# ADD ALL THE STADIUM NAMES TO THE DICTIONARY 
# (SAME PROCESS FOR ALL OF THE DATA BEING COLLECTED)
for i in stadium_index1:
    stadium = cells[i].get_text()
    stadium_data.setdefault("Stadium_Name", []).append(stadium)

final_stadiums = []
for i in stadium_index2:
    stadium2 = cells[i].get_text()
    final_stadiums.append(stadium2)

stadium_data["Stadium_Name"].extend(final_stadiums)

# INDEX 3 IS THE FIRST 121 TEAM NAMES
# INDEX 4 IS THE LAST 9 TEAM NAMES
index_list3 = list(range(4, 1331))
index_list4 = list(range(1334, 1429))
team_index1 = index_list3[0::11]
team_index2 = index_list4[0::11]
for i in team_index1:
    team = cells[i].get_text()
    stadium_data.setdefault("School", []).append(str(team))

final_teams = []
for i in team_index2:
    print(cells[i].get_text())
    #team2 = cells[i].get_text()
    #final_teams.append(team2)

stadium_data["School"].extend(str(final_teams))

# INDEX 5 IS THE FIRST 121 CAPACITIES
# INDEX 6 IS THE LAST 9 CAPACITIES 
index_list5 = list(range(6, 1331))
index_list6 = list(range(1336, 1430))
capacity_index1 = index_list5[0::11]
capacity_index2 = index_list6[0::11]
for i in capacity_index1:
    capacity = cells[i].get_text()
    new_values = capacity.split("[", 1)[0].replace(",", "") 
    stadium_data.setdefault("Capacity", []).append(int(new_values))

final_capacity = []
for i in capacity_index2:
    capacity2 = cells[i].get_text()
    new_values2 = capacity2.split("[", 1)[0].replace(",", "")
    final_capacity.append(int(new_values2))

stadium_data["Capacity"].extend(final_capacity)

stadium_df = pd.DataFrame(stadium_data, columns = stadium_data.keys())
'''

#####################################################################################
#       COLLECTING RECORD DATA FOR THE 2019 SEASON                                  #
#####################################################################################

my_url2 = "https://www.sports-reference.com/cfb/years/2019-standings.html"
uClient2 = urlopen(my_url2)
page_html2 = uClient2.read()
uClient2.close()

page_soup2 = soup(page_html2, "html.parser")

record_data = {}
schools = page_soup2.findAll("td", {"data-stat":"school_name"})
for school in schools:
    school_name = school.get_text()
    record_data.setdefault("School", []).append(school_name)

wins = page_soup2.findAll("td", {"data-stat":"wins"})
for win in wins:
    win_total = win.get_text()
    record_data.setdefault("Wins", []).append(int(win_total))

losses = page_soup2.findAll("td", {"data-stat":"losses"})
for loss in losses:
    loss_total = loss.get_text()
    record_data.setdefault("Losses", []).append(int(loss_total))

win_loss_pct = page_soup2.findAll("td", {"data-stat":"win_loss_pct"})
for elem in win_loss_pct:
    wl_percent = elem.get_text()
    record_data.setdefault("WL_Pct", []).append(float(wl_percent))

record_df = pd.DataFrame(record_data, columns = record_data.keys())


#######################################################################################
#       MERGING ALL OF THE SEPERATE DATA FRAMES                                       #
#######################################################################################
# CREATE A LIST OF ALL THE DATAFRAME NAMES
all_df = [record_df, salary_data, revenue_data]
# PERFORM AN INNER JOIN FOR ALL THE DATAFRAMES
# MATCH THEM BY SCHOOL NAME
salaries_df = reduce(lambda left, right: pd.merge(left, right, on = "School"), all_df)
# GET RID OF COMMAS AND THE $ FOR EACH ROW IN TOTALPAY
for i in list(range(0,99)):
    salaries_df["TotalPay"][i] = (salaries_df["TotalPay"][i].split("$", 0)[0].replace(",", "").replace("$", ""))
# CHANGE THE TYPE OF TOTALPAY TO INT TO PERFORM CALCULATIONS
salaries_df["TotalPay"] = salaries_df["TotalPay"].astype(str).astype(int)
# DROP THE COLUMNS WITH A BUNCH OF MISSING VALUES
# *** SCHOOL PAY IS BASICALLY THE SAME AS TOTAL PAY, ADDS NO VALUE FOR US ***
salaries_df.drop(["SchoolPay", "Bonus", "BonusPaid", "Buyout"], 
                 axis = 1, 
                 inplace = True)
# RENAME WIN LOSS COLUMNS BECASUE / WAS GIVING US ISSUES
salaries_df.rename({"W/L_Pct":"WL_Pct"}, axis = 1, inplace = True)
# ADD IN BOOLEAN COLUMN TO INDICTATE IF A TEAM IS IN A POWER 5 CONFERENCE
salaries_df["Power_5"] = salaries_df["Conference"].apply(lambda x: 1 if x in ["ACC", "Big Ten", "Big 12", "PAC-12", "SEC"] else 0)

###########################################################################################
#       EXPLORATORY DATA ANALYSIS AND VISUALIZATIONS                                                   #
###########################################################################################  
# MEAN OF ALL THE SALARIES 
print(round(salaries_df["TotalPay"].mean(), 2))

# MEAN OF ALL THE SALARIES BY CONFERENCE
salaries_df["TotalPay"].groupby(salaries_df["Conference"]).mean()
# MEAN OF THE REVENUE BY CONFERENCE
salaries_df["Revenue"].groupby(salaries_df["Conference"]).mean()


wins_BP = sns.boxplot(x = "Conference", 
                      y = "Wins", 
                      data = salaries_df)
plt.rc("xtick", labelsize = 5)
wins_BP.title("Wins per Conference")
       
 
salary_BP = sns.boxplot(x = "Conference", 
                        y = "TotalPay", 
                        data = salaries_df)

wins_salary_LP = sns.relplot(x = "Wins", 
                             y = "TotalPay", 
                             data = salaries_df, 
                             kind = "scatter",
                             hue = "Power_5")

revenue_BP = sns.boxplot(x = "Conference",
                         y = "Revenue",
                         data = salaries_df)

salary_revenue_LP = sns.relplot(x = "Revenue",
                                y = "TotalPay",
                                data = salaries_df,
                                kind = "scatter",
                                hue = "Power_5")

###########################################################################################
#       LINEAR MODEL                                                                      #
###########################################################################################

salaries_df["Conference"] = pd.Categorical(salaries_df["Conference"])

formula = str("TotalPay ~ Wins + Losses + WL_Pct + Conference + Revenue + Power_5")
model = smf.ols(formula, data = salaries_df).fit()
model.summary()

new_formula = str("TotalPay ~ Wins + Conference + Revenue + Power_5")
new_model = smf.ols(new_formula, data = salaries_df).fit()
new_model.summary()


def salary_prediction():
    wins = input("How many wins did your team have last year? ")
    revenue = input("What was the total revenue generated from your team last year? ")
    power_5 = input("Is your team in a power 5 conference? (ACC, Big12, BigTen, Pac12, SEC)[1 = Yes/0 = No] ")
    conference = input("What conference does your team play in? ")
    
    new_team = {"Wins": int(wins), "Revenue": int(revenue), "Power_5": int(power_5), "Conference": conference, "TotalPay": ""}
    prediction = new_model.predict(new_team)
    print("Projected Salary: ", int(prediction))

salary_prediction()
    
                    
 
   
  
   
   
