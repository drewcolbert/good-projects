# predicting if someone will have a stroke or not
library(caret)
library(naivebayes)
library(randomForest)
library(neuralnet)
library(corrplot)

########################################################################################################################################################
# READING IN THE DATA AND TRANSFORMING THE DATA TYPES
########################################################################################################################################################

# data was downloaded from the following site
# https://www.kaggle.com/fedesoriano/stroke-prediction-dataset
# change the file path and run the whole script


file_path <- "/Users/drewcolbert/Documents/Misc/stroke_data.csv"
stroke <- read.csv(file = file_path, header = TRUE, stringsAsFactors = FALSE)
str(stroke)

# get rid of the ID variable in the dataset (unused)
stroke <- stroke[,-1]
str(stroke)

# transform all of the data types in the data
stroke <- transform(stroke,
                    gender = as.factor(gender),
                    age = as.numeric(age),
                    hypertension = as.factor(hypertension),
                    heart_disease = as.factor(heart_disease),
                    ever_married = as.factor(ever_married),
                    work_type = as.factor(work_type),
                    Residence_type = as.factor(Residence_type),
                    avg_glucose_level = as.numeric(avg_glucose_level),
                    bmi = as.numeric(bmi),
                    smoking_status = as.factor(smoking_status),
                    stroke = as.factor(stroke))
str(stroke)

# there is only 1 case where gender = other, this could cause issues down the line with the modeling
# lets get rid of the one case where gender = other, if there were more cases of this I would leave it in
# first we want to remove the row where gender = other
stroke <- stroke[-which(as.character(stroke$gender) == "Other"),]
# then droplevels will drop that factor level from the data frame because there is no value to fill this factor level
stroke <- droplevels(stroke)
str(stroke)

# get rid of NAs
stroke <- na.omit(stroke)

########################################################################################################################################################
# DATA EXPLORATION
########################################################################################################################################################

# distributions of the dataset
# creates nine plots, showing the distributions of all the predicitve variables
par(mfrow = c(3,3))
hist(stroke$avg_glucose_level, main = "Avg Glucose Level", xlab = "", col = "orangered")
hist(stroke$bmi, main = "BMI", xlab = "", col = "orangered")
hist(stroke$age, main = "Age", xlab = "", col = "orangered")
barplot(table(stroke$gender), main = "Gender", col = "slateblue2")
barplot(table(stroke$hypertension), main = "Hypertension", col = "slateblue2", names.arg = c("Normal BP", "High BP"))
barplot(table(stroke$heart_disease), main = "Heart Disease", col = "slateblue2", names.arg = c("No", "Yes"))
barplot(table(stroke$ever_married), main = "Marital Staus", col = "gold", names.arg = c("Never Married", "Once Married"))
barplot(table(stroke$work_type), main = "Work History", col = "gold", names.arg = c("Stay at Home", "Gov", "Never Worked", "Private", "Self"))
barplot(table(stroke$smoking_status), main = "Smoking Status", col = "gold", names.arg = c("Formally", "Never", "Smoker", "Unknown"))

# shows three boxplots of the numeric variables in the dataset
# AGE -> older people tend to have many more strokes than younger people
# GLUCOSE -> there are a bunch of outliers in people that did not have a stroke, but most of them are around 75-120
# GLUCOSE -> the group that did have a stroke, had a much wider spread, but the medians are relatively close
# BMI -> the two groups are very similar, telling me BMI is not a big factor in determining whether a person will have a stroke or not
# BMI -> interestingly, the group who did not have a stroke had many more outliers that are much higher than the other group
par(mfrow = c(1,3))
boxplot(stroke$age ~ stroke$stroke, col = "firebrick", ylab = "", xlab = "0 = No, 1 = Yes", main = "Age")
boxplot(stroke$avg_glucose_level ~ stroke$stroke, col = "slateblue2", ylab = "", main = "Glucose Levels", xlab = "0 = No, 1 = Yes")
boxplot(stroke$bmi ~ stroke$stroke, col = "gold", ylab = "", main = "BMI", xlab = "0 = No, 1 = Yes")

# create a matrix with each category of smoking status and how many people had a stroke in each group
# since the "stroke" variable is binary, we can use the sum function and the total will be how many people had a stroke in each group
par(mfrow = c(2,2))
col_vec <- c("firebrick", "slateblue2", "gold", "forestgreen")
had_stroke <- stroke[stroke$stroke == 1,]
str(had_stroke)

stroke_and_smoke <- tapply(as.numeric(had_stroke$stroke), list(had_stroke$smoking_status), FUN = sum)
stroke_and_smoke
barplot(stroke_and_smoke, col = col_vec, names.arg = c("Formally", "Never", "Smoker", "Unknown"))

stroke_and_highbp <- tapply(as.numeric(had_stroke$stroke), list(had_stroke$hypertension), FUN = sum)
stroke_and_highbp
barplot(stroke_and_highbp, col = col_vec, names.arg = c("Normal BP", "High BP"))

stroke_and_work <- tapply(as.numeric(had_stroke$stroke), list(had_stroke$work_type), FUN = sum)
stroke_and_work
barplot(stroke_and_work, col = col_vec, names.arg = c("Stay at Home", "Gov", "Never Worked", "Private", "Self"))

stroke_and_gender <- tapply(as.numeric(had_stroke$stroke), list(had_stroke$gender), FUN = sum)
stroke_and_gender
barplot(stroke_and_gender, col = col_vec)

# these plots give us the counts of people who did have a stroke and also had each of these characteristics


########################################################################################################################################################
# MODELING THE DATA
########################################################################################################################################################

# take a random sample out of the data that is 70% of the data
train_data_size <- sample(nrow(stroke[,-1]), size = nrow(stroke) * 0.7, replace = FALSE)
# use the 70% as the training data
train_data <- stroke[train_data_size,]
# the other 30% is the testing data
test_data <- stroke[-train_data_size,]

# create plots to show the number of strokes in each new data frame to make sure it seems balanced
par(mfrow = c(1,3))
barplot(table(stroke$stroke), col = "firebrick", main = "Raw Data")
barplot(table(train_data$stroke), col = "firebrick", main = "Train Data")
barplot(table(test_data$stroke), col = "firebrick", main = "Test Data")
# all three data frames appear to have the same distribution of stroke victims to non-stroke victims

# train the KNN model
set.seed(24)
KNN_model1 <- train(stroke ~ .,
                    data = train_data,
                    method = "knn",
                    preProcess = c("center", "scale"))
KNN_model1
KNN_pred1 <- predict(KNN_model1, test_data)
KNN_confusion <- confusionMatrix(KNN_pred1, test_data[,11])

# train and test the naive bayes model
set.seed(24)
NB_model1 <- naive_bayes(stroke ~ .,
                         data = train_data,
                         laplace = 1)
NB_pred1 <- predict(NB_model1, test_data)
NB_confusion <- confusionMatrix(NB_pred1, test_data[,11])

# train and test the logistic regression model
set.seed(24)
LOG_model1 <- train(stroke ~., data = train_data, method = "bayesglm")
LOG_pred1 <- predict(LOG_model1, test_data)
LOG_confusion <- confusionMatrix(LOG_pred1, test_data[,11], positive = "1")

# train and test the random forest model
set.seed(24)
RF_model1 <- randomForest(stroke ~., data = train_data)
RF_pred1 <- predict(RF_model1, test_data)
RF_confusion <- confusionMatrix(RF_pred1, test_data[,11])




########################################################################################################################################################
# MODEL RESULTS AND COMPARISON
########################################################################################################################################################

# caluclate the accuracies of each model
KNN_acc <- ((KNN_confusion$table[1] + KNN_confusion$table[4])/sum(KNN_confusion$table)) * 100
NB_acc <- ((NB_confusion$table[1] + NB_confusion$table[4])/sum(NB_confusion$table)) * 100
LOG_acc <- ((LOG_confusion$table[1] + LOG_confusion$table[4])/sum(LOG_confusion$table)) * 100
RF_acc <- ((RF_confusion$table[1] + RF_confusion$table[4])/sum(RF_confusion$table)) * 100

# create a new different with the different model names and their accuracy scores
model_results <- data.frame(model = c("KNN", "NB", "LOG", "RF"), 
                            accuracy = c(KNN_acc, NB_acc, LOG_acc, RF_acc))
model_results

# plot the accuracies of each model
par(mfrow = c(1,1))
barplot(height = model_results$accuracy, 
        names.arg = model_results$model, 
        col = col_vec,
        ylim = c(0,100),
        main = "Model Accuracy Results",
        xlab = "Dashed Line Shows The No Information Rate")
# add a line to the plot showing the "no information rate"
abline(h = 95.72, lwd = 2, lty = "dashed")


sessionInfo()
