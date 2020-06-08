#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 17:50:14 2020

@author: drewcolbert
"""


from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq
import re
import urllib
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier

##############################################################################
#           CREATING THE LIST OF PLAYER NAMES TO ENTER INTO THE URL          #
##############################################################################
# open the url using urlopen
my_url = "https://www.mlb.com/players"
uClient = uReq(my_url)
page_html = uClient.read()
uClient.close()

# CREATE A PARSER TO GO THROUGH THE HTML TEXT 
page_soup = soup(page_html, "html.parser")

# FIND ALL HTML LINKS FOR EVERY PLAYER ON THE WEBSITE 
containers = page_soup.findAll("a", {"class":"p-related-links__link"})


# "CONTENTS" GIVES US THE LABELS FOR EACH REFERENCE LINK ("HREF" IN HTML) 
player_names = []
for container in containers:
    name = re.sub("[|[|'|]|]", "", str(container.contents))
    newname = name.split(" ")
    player_names.append(newname)
del(player_names[1868])

# PUT THE PLAYERS FIRST AND LAST NAMES INTO SEPERATE LISTS 
firstname = []
lastname = []
for line in player_names:
    firstname.append(line[0])

for line in player_names:
    lastname.append(line[1])

# CREATE THE NAMES THAT WILL GO INTO THE URL 
part1 = []
for elem in firstname:
    fname = elem[0:2].lower()
    part1.append(fname)
part2 = []
for elem in lastname:
    lname = elem[0:5].lower()
    part2.append(lname)
lookup_name = []
for i in range(0, len(player_names)):
    url_name = part2[i] + part1[i] + "01"
    lookup_name.append(url_name)
    
##############################################################################
#               GATHERING THE DATA FOR EACH CURRENT PLAYER                   #
##############################################################################
# THIS CODE PUTS STATS INTO A DICT 
# EACH KEY HAS A LIST OF VALUES FOR EACH PLAYER
stats = {}
for x in range(0, len(lookup_name)):
    try:
        # RUNS THROUGH EACH LOOKUP NAME TO REQUEST EACH URL 
        stats_url = f"https://www.baseball-reference.com/players/{lookup_name[x][0]}/{lookup_name[x]}.shtml".encode()
        response = uReq(stats_url.decode("ASCII", errors = "ignore"))
        stats_html = response.read()
        response.close()
    # IF THE WEBSITE IS NOT FOUND, WE IGNORE IT AND MOVE ON 
    except urllib.error.HTTPError as err:
        if err.code == 404:
            continue
    stats_soup = soup(stats_html, "html.parser")
    # IF THE WEBSITE IS GOOD, WE CHECK FOR THE PLAYERS POSITION
    baskets = stats_soup.find("div", {"id":"meta"})
    for basket in baskets:
        t = baskets.findAll("p")
        # GETS THE TEXT FROM THE P TAG AND SPLITS IT INTO A LIST
        # ["POSITION:", "(PLAYER POSITION)"]
        pos_text = t[0].get_text().split()
        # IF THE PLAYER IS A PITCHER, WE IGNORE THEIR STATS AND MOVE ON
        if pos_text[0] == "Pitcher" or pos_text[1] == "Pitcher":
            continue
        else:
            try:
                # RETRIEVES ALL TAGS CONTAINING THE STATS 
                # AND ADDS THEM TO A DICITONARY 
                stats1 = stats_soup("div", {"class":"p1"})
                for stat1 in stats1:
                    item1 = stat1.findAll("p")
                    # ON THE WEBISTE, FORMER PLAYERS DID NOT HAVE STATS 
                    # FROM THE MOST RECENT MLB SEASON, SO THE NUMBER OF 
                    # P TAGS FOUND WOULD BE LESS THAN THOSE OF CURRENT PLAYERS
                    if len(item1) < 10:
                        continue
                    else:
                        stats.setdefault("WAR", []).append(float(item1[1].get_text()))
                        stats.setdefault("At Bats", []).append(float(item1[3].get_text()))
                        stats.setdefault("Hits", []).append(float(item1[5].get_text()))
                        stats.setdefault("HR", []).append(float(item1[7].get_text()))
                        stats.setdefault("Average", []).append(float(item1[9].get_text()))
                stats2 = stats_soup("div", {"class":"p2"})
                for stat2 in stats2:
                    item2 = stat2.findAll("p")
                    if len(item2) < 6:
                        continue
                    else:
                        stats.setdefault("Runs", []).append(float(item2[1].get_text()))
                        stats.setdefault("RBI", []).append(float(item2[3].get_text()))
                        stats.setdefault("SB", []).append(float(item2[5].get_text()))
                stats3 = stats_soup("div", {"class":"p3"})
                for stat3 in stats3:
                    item3 = stat3.findAll("p")
                    if len(item3) < 8:
                        continue
                    else:
                        stats.setdefault("OBP", []).append(float(item3[1].get_text()))
                        stats.setdefault("SLG", []).append(float(item3[3].get_text()))
                        stats.setdefault("OPS", []).append(float(item3[5].get_text()))
            # SOMETIMES THERE IS AN ERROR WHERE THE INDEX IS OUT OF RANGE
            # COULD BE BECAUSE THEY ARE A ROOKIE AND DO NOT HAVE ANY STATS LISTED
            # WHATEVER THE CASE, WE WANT TO IGNORE THAT PLAYER AND MOVE TO THE NEXT
            except IndexError:
                continue

# THE ABOVE CODE GIVES US 5 OF EACH STAT FOR EACH PLAYER
# WE ONLY WANT ONE PER PLAYER SO THIS CODE GIVES US EVERY 5TH ELEMENT IN THE LIST
# AND RETURNS IT BACK INTO THE ORIGINAL KEY IN THE DICTIONARY
stats["WAR"] = stats["WAR"][::5]
stats["At Bats"] = stats["At Bats"][::5]
stats["Hits"] = stats["Hits"][::5]
stats["HR"] = stats["HR"][::5]
stats["Average"] = stats["Average"][::5]
stats["OBP"] = stats["OBP"][::5]
stats["OPS"] = stats["OPS"][::5]
stats["RBI"] = stats["RBI"][::5]
stats["Runs"] = stats["Runs"][::5]
stats["SB"] = stats["SB"][::5]
stats["SLG"] = stats["SLG"][::5]


##############################################################################
#               CREATING THE DATAFRAMES                                      #
##############################################################################

player_data = pd.DataFrame(stats, columns = ["WAR", "At Bats", "Hits", "HR", "Average", "RBI", "Runs", "SB", "SLG", "OBP", "OPS"])
hof_data = pd.read_csv(r"hof_data.csv")
# ADDING IF THEY ARE IN THE HALL OF FAME OR NOT TO THE DF
player_data["HOF?"] = 0
hof_data["HOF?"] = 1

# ADDING HALL OF FAME DATA TO THE CURRENT PLAYER DATA 
stats["WAR"].extend(hof_data["WAR"])
stats["Average"].extend(hof_data["Average"])
stats["HR"].extend(hof_data["HR"])
stats["Hits"].extend(hof_data["Hits"])
stats["At Bats"].extend(hof_data["At Bats"])
stats["OBP"].extend(hof_data["OBP"])
stats["OPS"].extend(hof_data["OPS"])
stats["RBI"].extend(hof_data["RBI"])
stats["Runs"].extend(hof_data["Runs"])
stats["SB"].extend(hof_data["SB"])
stats["SLG"].extend(hof_data["SLG"])
stats["HOF?"] = []
stats["HOF?"].extend(player_data["HOF?"])
stats["HOF?"].extend(hof_data["HOF?"])

# CREATING ONE DATAFRAME WITH BOTH CURRENT AND HALL OF FAME PLAYER STATS
all_player_data = pd.DataFrame(stats, columns = ["At Bats", "Average", "Hits", "HR", "RBI", "Runs", "OBP", "OPS", "SLG", "SB", "WAR", "HOF?"])

# FIND THE TOP 25% FOR TOTAL AT BATS 
arr = [player_data["At Bats"]]
quantiles = player_data.quantile(q = .75, axis = 0)
# CREATING A DATAFRAME WITH JUST THE PLAYERS IN THE TOP 25% FOR AT BATS
top_25 = player_data.loc[(player_data["At Bats"] >= 2389),:]
top_25["HOF?"] = 0
# COMBINING THE HALL OF FAME DF WITH THE TOP 25% DF
top_players_df = pd.concat([top_25, hof_data], ignore_index = True)


##############################################################################
#               EXPLORATORY DATA ANALYSIS                                    #
##############################################################################
print("Average BA of current players: ", round(player_data["Average"].mean(), 3))
print("Average BA of HOF players: ", round(hof_data["Average"].mean(), 3))
print("\nAverage AB of current players: ", round(player_data["At Bats"].mean(), 0))
print("Average AB of HOF players: ", round(hof_data["At Bats"].mean(), 0))
print("\nAverage career hit totals by current players: ", round(player_data["Hits"].mean(), 0))
print("Average career hit totals by HOF players: ", round(hof_data["Hits"].mean(), 0))
print("\nAverage career RBIs for current players: ", round(player_data["RBI"].mean(), 0))
print("Average career RBIs for HOF players: ", round(hof_data["RBI"].mean(), 0))
print("\nAverage HR hit by current players: ", round(player_data["HR"].mean(), 0))
print("Average HR hit by HOF players: ", round(hof_data["HR"].mean(), 0))
print("\nAverage runs scored by current players: ", round(player_data["Runs"].mean(), 0))
print("Average runs scored HOF players: ", round(hof_data["Runs"].mean(), 0))
print('\n========================================================')
print("Average number of stolen bases for current players: ", round(player_data["SB"].mean(), 0))
print("Average number of stolen bases for HOF players: ", round(hof_data["SB"].mean(), 0))
print("\nAverage OBP for current players: ", round(player_data["OBP"].mean(), 3))
print("Average OBP for HOF players: ", round(hof_data["OBP"].mean(), 3))
print("\nAverage slugging percentage for current players: ", round(player_data["SLG"].mean(), 3))
print("Average slugging percentage for HOF players: ", round(hof_data["SLG"].mean(), 3))
print("\nAverage OPS for current players: ", round(player_data["OPS"].mean(), 3))
print("Average OPS for HOF players: ", round(hof_data["OPS"].mean(), 3))
print("\nAverage WAR of current players: ", round(player_data["WAR"].mean(), 1))
print("Average WAR of HOF players: ", round(hof_data["WAR"].mean(), 1))


print("Average BA of top players: ", round(top_25["Average"].mean(), 3))
print("Average BA of HOF players: ", round(hof_data["Average"].mean(), 3))
print("\nAverage AB of top players: ", round(top_25["At Bats"].mean(), 0))
print("Average AB of HOF players: ", round(hof_data["At Bats"].mean(), 0))
print("\nAverage career hit totals by top players: ", round(top_25["Hits"].mean(), 0))
print("Average career hit totals by HOF players: ", round(hof_data["Hits"].mean(), 0))
print("\nAverage career RBIs for top players: ", round(top_25["RBI"].mean(), 0))
print("Average career RBIs for HOF players: ", round(hof_data["RBI"].mean(), 0))
print("\nAverage HR hit by top players: ", round(top_25["HR"].mean(), 0))
print("Average HR hit by HOF players: ", round(hof_data["HR"].mean(), 0))
print("\nAverage runs scored by top players: ", round(top_25["Runs"].mean(), 0))
print("Average runs scored HOF players: ", round(hof_data["Runs"].mean(), 0))
print('\n============================================================')
print("\nAverage number of stolen bases for top players: ", round(top_25["SB"].mean(), 0))
print("Average number of stolen bases for HOF players: ", round(hof_data["SB"].mean(), 0))
print("\nAverage OBP for top players: ", round(top_25["OBP"].mean(), 3))
print("Average OBP for HOF players: ", round(hof_data["OBP"].mean(), 3))
print("\nAverage slugging percentage for top players: ", round(top_25["SLG"].mean(), 3))
print("Average slugging percentage for HOF players: ", round(hof_data["SLG"].mean(), 3))
print("\nAverage OPS for top players: ", round(top_25["OPS"].mean(), 3))
print("Average OPS for HOF players: ", round(hof_data["OPS"].mean(), 3))
print("\nAverage WAR of top players: ", round(top_25["WAR"].mean(), 1))
print("Average WAR of HOF players: ", round(hof_data["WAR"].mean(), 1))



print(top_players_df.groupby("HOF?").mean())
print(top_25.describe())
print(hof_data.describe())


##############################################################################
#               KNN MODEL                                                    #
##############################################################################
# X IS ALL THE ATTRIBUTES
# y IS THE LABELS (HOF OR NOT)
y = all_player_data.iloc[:,11]
X = all_player_data.iloc[:,:11]

# CREATING TRAINING AND TESTING DATA 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.20, random_state = 10)

# CALCULATING ERROR RATES FOR 40 VALUES OF K 
error_rate = []
for i in range(1,40):
    knn = KNeighborsClassifier(n_neighbors = i)
    knn.fit(X_train, y_train)
    pred_i = knn.predict(X_test)
    error_rate.append(np.mean(pred_i != y_test))

# PLOT THE ERROR RATES FOR EACH VALUE OF K
plt.plot(range(1,40), error_rate, color = 'blue', linestyle = 'dashed', marker = 'o')
plt.title('Error Rate vs K')
plt.xlabel('K')
plt.ylabel('Error Rate')

# MAKING THE KNN MODEL
classifier = KNeighborsClassifier(n_neighbors = 6, metric = 'minkowski')
classifier.fit(X_train, y_train)
KNN_pred = classifier.predict(X_test)
# DISPLAY CONFUSION MATRIX AND CLASSIFICATION REPORT
print(confusion_matrix(y_test, KNN_pred))
print(classification_report(y_test, KNN_pred))


# FUNCTION THAT ALLOWS YOU TO ENTER A PLAYERS CAREER
# STATS AND PREDICT WHETHER THEY WILL BE IN THE HOF OR NOT
def predict_hof_KNN():
    player = input("Player name: ")
    print("\nWill", player, "be a hall of famer?")
    ave = input("Player's career BA: ")
    ab = input("Player's career ABs: ")
    hits = input("Player's career hits: ")
    rbi = input("Player's total RBI count: ")
    hr = input("Player's total HR count: ")
    runs = input("Player's total runs scored: ")
    sb = input("Player's total stolen bases: ")
    obp = input("Player's career OBP: ")
    slg = input("Player's career slugging percentage: ")
    ops = input("Player's career OPS: ")
    war = input("Player's career WAR: ")
    
    new_player_stats = {}
    new_player_stats.setdefault("Average", []).append(float(ave))
    new_player_stats.setdefault("At Bats", []).append(float(ab))
    new_player_stats.setdefault("HR", []).append(float(hr))
    new_player_stats.setdefault("Hits", []).append(float(hits))
    new_player_stats.setdefault("OBP", []).append(float(obp))
    new_player_stats.setdefault("OPS", []).append(float(ops))
    new_player_stats.setdefault("RBI", []).append(float(rbi))
    new_player_stats.setdefault("Runs", []).append(float(runs))
    new_player_stats.setdefault("SB", []).append(float(sb))
    new_player_stats.setdefault("SLG", []).append(float(slg))
    new_player_stats.setdefault("WAR", []).append(float(war))
    
    new_testing = pd.DataFrame(new_player_stats, columns = ["WAR", "At Bats", "Hits", "HR", "Average", "RBI", "Runs", "SB", "SLG", "OBP", "OPS"])
    
    new_prediction = classifier.predict(new_testing)
    if new_prediction[0] == 1:
        print("\nCongrats!", player, "is on his way to being in the Hall of Fame.")
    else:
        print("\nUh oh...", player, "needs to step up his game.")

predict_hof_KNN()


##############################################################################
#           RANDOM FOREST ALGORITHM                                          #
##############################################################################
# FINDING THE BEST PARAMETERS FOR OUR RANDOM FOREST MODEL
# N_ESTIMATORS = NUMBER OF TREES IN THE FOREST 
# WE ARE TRYING EVERY 10 NUMBERS FROM 20-2000
n_estimators = [int(x) for x in np.linspace(start = 200, stop = 2000, num = 10)]
# MAX_FEATURES = NUMBER OF FEATURES CONSDIERED AT EACH SPLIT
max_features = ['auto', 'sqrt']
# MAX_DEPTH = MAXIMUM NUMBER OF LEVELS IN A TREE
max_depth = [int(x) for x in np.linspace(10, 110, num = 11)]
max_depth.append(None)
# MIN_SAMPLES_SPLIT = MIN NUMBER OF SAMPLES REQUIRED TO SPLIT A NODE
min_samples_split = [2, 5, 10]
# MIN_SAMPLES_LEAF = MIN NUMBER OF SAMPLES REQUIRED AT EACH LEAF NODE
min_samples_leaf = [1, 2, 4]
# BOOTSTRAP = METHOD OF SELECTING SAMPLES FOR TRAINING EACH TREE
bootstrap = [True, False]

# CREATE THE DICTIONARY FOR EACH PARAMETER 
random_grid = {'n_estimators': n_estimators, 'max_features': max_features, 'max_depth': max_depth, 'min_samples_split': min_samples_split, 'min_samples_leaf': min_samples_leaf, 'bootstrap': bootstrap}

# RUN THROUGH 100 DIFFERENT ITERATIONS USING RANDOM VALUES FROM THE ABOVE DICT
# RUN 5-FOLD CV FOR EACH ITERATION, PRINTS OUT THE BEST PARAMETER VALUES
rf = RandomForestClassifier()
rf_random = RandomizedSearchCV(estimator = rf, param_distributions = random_grid, n_iter = 100, cv = 5, verbose = 2, random_state = 42, n_jobs = -1)
rf_random.fit(X_train, y_train)
print(rf_random.best_params_)

# CREATING THE RANDOM FOREST MODEL
rf_classifier = RandomForestClassifier(n_estimators = 2000, min_samples_split = 2, min_samples_leaf = 4, max_features = 'auto', max_depth = 30, bootstrap = False)
rf_classifier.fit(X_train,y_train)
rf_pred = rf_classifier.predict(X_test)
print(round(rf_classifier.score(X_test,y_test), 4))
print(rf_classifier.feature_importances_)

# FUNCTION THAT ALLOWS YOU TO ENTER A PLAYERS CAREER
# STATS AND PREDICT WHETHER THEY WILL BE IN THE HOF OR NOT
def predict_hof_RF():
    player = input("Player name: ")
    print("\nWill", player, "be a hall of famer?")
    ave = input("Player's career BA: ")
    ab = input("Player's career ABs: ")
    hits = input("Player's career hits: ")
    rbi = input("Player's total RBI count: ")
    hr = input("Player's total HR count: ")
    runs = input("Player's total runs scored: ")
    sb = input("Player's total stolen bases: ")
    obp = input("Player's career OBP: ")
    slg = input("Player's career slugging percentage: ")
    ops = input("Player's career OPS: ")
    war = input("Player's career WAR: ")
    
    new_player_stats = {}
    new_player_stats.setdefault("Average", []).append(float(ave))
    new_player_stats.setdefault("At Bats", []).append(float(ab))
    new_player_stats.setdefault("HR", []).append(float(hr))
    new_player_stats.setdefault("Hits", []).append(float(hits))
    new_player_stats.setdefault("OBP", []).append(float(obp))
    new_player_stats.setdefault("OPS", []).append(float(ops))
    new_player_stats.setdefault("RBI", []).append(float(rbi))
    new_player_stats.setdefault("Runs", []).append(float(runs))
    new_player_stats.setdefault("SB", []).append(float(sb))
    new_player_stats.setdefault("SLG", []).append(float(slg))
    new_player_stats.setdefault("WAR", []).append(float(war))
    
    new_testing = pd.DataFrame(new_player_stats, columns = ["WAR", "At Bats", "Hits", "HR", "Average", "RBI", "Runs", "SB", "SLG", "OBP", "OPS"])
    
    new_prediction = rf_classifier.predict(new_testing)
    if new_prediction[0] == 1:
        print("\nCongrats!", player, "is on his way to being in the Hall of Fame.")
    else:
        print("\nUh oh...", player, "needs to step up his game.")

predict_hof_RF()



        


  

    
    
    
    
    
    
    
    
    
    
    