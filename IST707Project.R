# READ IN THE DATA
vg_data <- read.csv("~/Downloads/vgsales.csv")
vg_data2 <- read.csv("~/Downloads/chggamesales.csv")


#####################################################################################################
#   ASSOCIATTION RULES                                                                              #
#####################################################################################################
library("arules")
update.packages("arules")
# BIN THE GLOBAL SALES
vg_data <- vg_data[,-7:-10]
vg_data <- vg_data[which(vg_data$Global_Sales >= .500),]
vg_data$Global_Sales <- cut(vg_data$Global_Sales, breaks = c(0, .70, 1.500, 41.00), labels = c("Low", "Decent", "High"))
vg_data <- vg_data[-1,]

summary(vg_data$Global_Sales)
vg_data2 <- na.omit(vg_data2)
vg_data2 <- vg_data2[,c(-1,-3)]
vg_data2 <- vg_data2[which(vg_data2$Global_Sales >= .500),]
vg_data2$Global_Sales <- cut(vg_data2$Global_Sales, breaks = c(0, .500, 1.000, 10.000, 20.000, 83.000), labels = c("Low", "Decent", "High", "Very High", "Top Seller"))
str(vg_data2)
vg_data2
summary(vg_data2)
# WRITE OUT A NEW CSV WITH THE BINNED GLOBAL SALES
write.csv(vg_data, file = "/Users/drewcolbert/Documents/newvg_data.csv")

# READ IN THE NEW FILE 
newvg_data <- read.csv("~/Documents/newvg_data.csv")
# GET RID OF THE RANK AND ID COLUMNS AND WII SPORTS
newvg_data <- newvg_data[,-1:-2]
newvg_data <- newvg_data[-1,]

# PLAY AROUND WITH THE SUPPORT AND CONFIDENCE TO FIND RULES 
vg_rules <- apriori(vg_data, parameter = list(support = 0.01, conf = 0.5, minlen = 3))
inspect(vg_rules[1:10])
summary(newvg_data$Publisher)


#####################################################################################################
#       NAIVE BAYES
#####################################################################################################
install.packages("naivebayes")
library("naivebayes")

samples = sample(nrow(newvg_data), 0.66*nrow(newvg_data))
vg_NB_Train <- newvg_data[samples,]
vg_NB_Test <- newvg_data[-samples,]

# NB USING ALL COLUMNS IN THE DF
NB_model1 <- naive_bayes(Global_Sales ~., vg_NB_Train, laplace = 1)
NB_pred <- predict(NB_model1, vg_NB_Test, type = c("class"))
table(vg_NB_Test$Global_Sales, NB_pred)
plot(NB_model1)

# NB USING JUST THE PUBLISHER
NB_model2 <- naive_bayes(Global_Sales ~ Publisher, vg_NB_Train, laplace = 1)
NB_pred2 <- predict(NB_model2, vg_NB_Test, type = c("class"))
table(vg_NB_Test$Global_Sales, NB_pred2)
plot(NB_model2)

#NB USING JUST THE GENRE 
NB_model3 <- naive_bayes(Global_Sales ~ Genre, vg_NB_Train, laplace = 1)
NB_pred3 <- predict(NB_model3, vg_NB_Test, type = c("class"))
NBpred_table <- table(vg_NB_Test$Global_Sales, NB_pred3)
NBpred_table
NBmodel_acc <- ((NBpred_table[1,1] + NBpred_table[2,2] + NBpred_table[3,3])/1366)*100
NBmodel_acc
par(las = 1)
plot(NB_model3)
summary(vg_data$Genre)


###########################################################################################
#     RANDOM FOREST                                                                       # 
###########################################################################################
library(randomForest)
vg_rf <- randomForest(Global_Sales ~ Platform + Year + Genre, vg_data)
print(vg_rf)
legend("bottomleft", legend = c("1","2","3","4"))
rf_plot <- plot(vg_rf)
?plot()



#####################################################################################################
#     GRAPHING THE SALES PER CONSOLE                                                                #
#####################################################################################################
library(ggplot2)
# READ IN THE DATA WITH CONSOLES AND DECADES ALREADY BINNED
vg_data_unbinned <- read.csv("~/Documents/Programs/chggamesales.csv")
vg_data_unbinned <- vg_data_unbinned[which(vg_data_unbinned$Global_Sales >= .500),]
vg_data_unbinned <- vg_data_unbinned[-max(vg_data_unbinned$Global_Sales),]
 
# SUM THE SALES BY DECADE FOR EACH CONSOLE
atari_group <- vg_data_unbinned[which(vg_data_unbinned$Consoles == "Atari"),] 
atari_sales <- aggregate(x = atari_group$Global_Sales, by = list(atari_group$Decade), FUN= sum)

GC_group <- vg_data_unbinned[which(vg_data_unbinned$Consoles == "GC"),]
GC_sales <- aggregate(x = GC_group$Global_Sales, by = list(GC_group$Decade), FUN= sum)

handheld_group <- vg_data_unbinned[which(vg_data_unbinned$Consoles == "Handheld"),]
handheld_sales <- aggregate(x = handheld_group$Global_Sales, by = list(handheld_group$Decade), FUN= sum)

nintendo_group <- vg_data_unbinned[which(vg_data_unbinned$Consoles == "Nintendo"),]
nintendo_sales <- aggregate(x = nintendo_group$Global_Sales, by = list(nintendo_group$Decade), FUN= sum)

pc_group <- vg_data_unbinned[which(vg_data_unbinned$Consoles == "PC"),]
pc_sales <- aggregate(x = pc_group$Global_Sales, by = list(pc_group$Decade), FUN= sum)

ps_group <- vg_data_unbinned[which(vg_data_unbinned$Consoles == "PS"),]
ps_sales <- aggregate(x = ps_group$Global_Sales, by = list(ps_group$Decade), FUN= sum)

sega_group <- vg_data_unbinned[which(vg_data_unbinned$Consoles == "Sega"),]
sega_sales <- aggregate(x = sega_group$Global_Sales, by = list(sega_group$Decade), FUN= sum)

wii_group <- vg_data_unbinned[which(vg_data_unbinned$Consoles == "Wii"),]
wii_sales <- aggregate(x = wii_group$Global_Sales, by = list(wii_group$Decade), FUN= sum)

xbox_group <- vg_data_unbinned[which(vg_data_unbinned$Consoles == "Xbox"),]
xbox_sales <- aggregate(x = xbox_group$Global_Sales, by = list(xbox_group$Decade), FUN= sum)

# CREATE A NEW DATAFRAME WITH THE SALES PER DECADE FOR EACH CONSOLE
consoles <- c("Atari", "Atari", "GC", "Handheld", "Handheld", "Handheld", "Handheld", "Nintendo", "Nintendo", "Nintendo", "PC", "PC", "PC", "PS", "PS", "PS", "Sega", "Sega", "Wii", "Wii", "Xbox", "Xbox")
decade <- c("1970", "1980", "2000", "1980", "1990", "2000", "2010", "1980", "1990", "2000", "1990", "2000", "2010", "1990", "2000", "2010", "1990", "2000", "2000", "2010", "2000", "2010")
total_sales <- c(4.76, 69.61, 129.88, 66.41, 154.26, 757.76, 265.50, 221.55, 337.49, 27.44, 49.06, 63.42, 79.99, 481.43, 1555.03, 806.51, 42.34, 4.04, 582.45, 240.72, 509.04, 605.51)
global_sales_by_decade <- data.frame(consoles, decade, total_sales, stringsAsFactors = FALSE)

sales_per_console <- ggplot(global_sales_by_decade, aes(x = consoles, y = total_sales, color = decade, fill = decade)) + geom_bar(stat = 'identity')
sales_per_console <- sales_per_console + ggtitle("Sales per Console for Each Decade")
sales_per_console


###########################################################################################
#     FINDING THE SALES PER ONE GAME FOR EACH CONSOLE                                     #
###########################################################################################
library('plyr')
library('ggplot2')
# COUNTS HOW MANY TIMES EACH CONSOLE APPEARS IN THE DATA
count(vg_data2, 'Consoles')

# SUM OF SALES DIVIDED BY THE NUMBER OF GAMES 
atari_salesPer_game <- sum(atari_group$Global_Sales)/60
GC_salesPer_game <- sum(GC_group$Global_Sales)/96
handheld_salesPer_game <- sum(handheld_group$Global_Sales)/615
nintendo_salesPer_game <- sum(nintendo_group$Global_Sales)/263
pc_salesPer_game <- sum(pc_group$Global_Sales)/122
ps_salesPer_game <- sum(ps_group$Global_Sales)/1787
sega_salesPer_game <- sum(sega_group$Global_Sales)/30
wii_salesPer_game <- sum(wii_group$Global_Sales)/369
xbox_salesPer_game <- sum(xbox_group$Global_Sales)/676

Consoles <- c("Atari", "GC", "Handheld", "Nintendo", "PC", "PS", "Sega", "Wii", "Xbox")
Sales_Per_Game <- c(atari_salesPer_game, GC_salesPer_game, handheld_salesPer_game, nintendo_salesPer_game, pc_salesPer_game, ps_salesPer_game, sega_salesPer_game, wii_salesPer_game, xbox_salesPer_game)
Number_Of_Games <- c(60, 96, 615, 263, 122, 1787, 30, 369, 676)
sales_per_game_df <- data.frame(Consoles, Number_Of_Games, Sales_Per_Game)
sales_per_game_df

sales_per_game_graph <- ggplot(sales_per_game_df, aes(x = Consoles, y = Sales_Per_Game, fill = Number_Of_Games)) + geom_bar(stat = 'identity')
sales_per_game_graph <- sales_per_game_graph + ggtitle("Sales per Game for Each Console")
sales_per_game_graph


install.packages("wordcloud")
install.packages("tm")
library("wordcloud")
library("dplyr")
library("tm")
top10 <- head(vg_data[order(vg_data$Global_Sales, decreasing=TRUE), ], 1660)
word.vec1 <- VectorSource(top10$Name)
words.corpus1 <- Corpus(word.vec1)
words.corpus1
words.corpus1 <- tm_map(words.corpus1, content_transformer(tolower))
words.corpus1 <- tm_map(words.corpus1, removePunctuation)
words.corpus1 <- tm_map(words.corpus1, removeNumbers)
words.corpus1 <- tm_map(words.corpus1, removeWords, stopwords("english"))
tdm1 <- TermDocumentMatrix(words.corpus1)
tdm1
m1 <- as.matrix(tdm1)
wordCounts1 <- rowSums(m1)
wordCounts1 <- sort(wordCounts1, decreasing =TRUE)
head(wordCounts1)
cloudframe1 <- data.frame(word=names(wordCounts1), freq=wordCounts1)
wordcloud::wordcloud(cloudframe1$word, cloudframe1$freq)
wordcloud::wordcloud(names(wordCounts1), wordCounts1, min.freq = 3, max.words = 50, rot.per = .25)

head(vg_data)




library(rpart)
library(randomForest)

samples = sample(nrow(vg_data2), 0.66*nrow(vg_data2)) 
vg_rf_Train <- vg_data2[samples,] 
vg_rf_Test <- vg_data2[-samples,] 
na.omit(vg_rf_Train)
na.omit(vg_rf_Test)
tree2 <- rpart(Global_Sales~ Consoles + Year + Genre, data = vg_rf_Train, method = "class", minsplit = 10, minbucket = 5) 
trepre <- predict(tree2, vg_rf_Test[,-7]) 
cm <- table(vg_rf_Test[,7],trepre) 
cm 











