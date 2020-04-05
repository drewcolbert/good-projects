mywinedata <- read.csv("~/Downloads/winequality-white.csv", sep=";", stringsAsFactors = FALSE)
mywinedata <- mywinedata[,-1:-3]
mywinedata <- mywinedata[,-6:-7]
mywinedata
#summary of dataset
summary(winequality.white)

#group together the high quality wines (7, 8, 9)
highquality <- winequality.white[which(winequality.white$quality >= 7),]

#group together the low quality wines (3,4,5,6)
lowquality <- winequality.white[which(winequality.white$quality <= 6),]

#histograms of all the columns
par(mfrow = c(2,3))
hist(winequality.white$residual.sugar)
hist(winequality.white$chlorides)
hist(winequality.white$free.sulfur.dioxide)
hist(winequality.white$total.sulfur.dioxide)
hist(winequality.white$density)
hist(winequality.white$alcohol)

library("randomForest")
#randomForest of wines (classification)
quality.rf <- randomForest(as.factor(quality) ~ fixed.acidity + volatile.acidity + citric.acid + residual.sugar + chlorides + free.sulfur.dioxide + total.sulfur.dioxide + density + pH + sulphates + alcohol, data= winequality.white)
quality.rf
importance(quality.rf)
varImpPlot(quality.rf, main= "Importance Plot") 

#histograms of the high quality dataset
par(mfrow = c(3,4))
hist(winequality.white$residual.sugar, main= "Residual Suagar")
hist(winequality.white$chlorides, main= "Chlorides")
hist(winequality.white$free.sulfur.dioxide, main= "Free Sulfur Dioxide")
hist(winequality.white$total.sulfur.dioxide, main= "Total Sulfur Dioxide")
hist(winequality.white$density, main= "Density")
hist(winequality.white$alcohol, main= "Alcohol")
hist(winequality.white$fixed.acidity, main= "Fixed Acidity")
hist(winequality.white$volatile.acidity, main= "Volatile Acidity")
hist(winequality.white$citric.acid, main= "Citric Acid")
hist(winequality.white$pH, main= "pH")
hist(winequality.white$sulphates, main= "Sulphates")
hist(winequality.white$quality, main = "Quality")

#take a random sample of 100 rows from high quality and low quality 
install.packages("dpylr")
install.packages("ggpubr")
library("dpylr")
library("ggpubr")
lqsamp <- dplyr::sample_n(lowquality,100)
hqsamp <- dplyr::sample_n(highquality,100)

#run a paired t-test for each column to determine any differences between means 
t.test(lqsamp[,1],hqsamp[,1],paired=TRUE)
t.test(lqsamp[,2],hqsamp[,2],paired=TRUE)
t.test(lqsamp[,3],hqsamp[,3],paired=TRUE)
t.test(lqsamp[,4],hqsamp[,4],paired=TRUE)
t.test(lqsamp[,5],hqsamp[,5],paired=TRUE)
t.test(lqsamp[,6],hqsamp[,6],paired=TRUE)
t.test(lqsamp[,7],hqsamp[,7],paired=TRUE)
t.test(lqsamp[,8],hqsamp[,8],paired=TRUE)
t.test(lqsamp[,9],hqsamp[,9],paired=TRUE)
t.test(lqsamp[,10],hqsamp[,10],paired=TRUE)
t.test(lqsamp[,11],hqsamp[,11],paired=TRUE)

#create a new data frame with only the columns with a significant difference 
hqsigdif <- highquality[,c(-1,-2,-3,-4,-6,-9,-10)]
lqsigdif <- lowquality[,c(-1,-2,-3,-4,-6,-9,-10)]

#run a randomForest of the signifcant columns for low and high quality data frames
library(randomForest)
hq1 <- randomForest(as.factor(quality) ~., data= highquality, importance = TRUE)
hq1
importance(hq1)
varImpPlot(hq1, main= "High Quality Importance")
hqrfpred <- predict(hq1, winequality.white)
lq1 <- randomForest(as.factor(quality) ~., data= lowquality, importance= TRUE)
lq1
importance(lq1)
varImpPlot(lq1, main= "Low Quality Importance")

#neural network 
install.packages("neuralnet")
library("neuralnet")
nndata <- winequality.white
nn <- neuralnet(quality ~ ., nndata, hidden = 3, linear.output = FALSE, threshold = .01)
plot(nn)

#ksvm testing 
install.packages("kernlab")
library("kernlab")
winequality.white$highorlow <- ifelse(winequality.white$quality >= 7, "yes", "no")
winequality.white$highorlow <- as.factor(winequality.white$highorlow)
nrows <- nrow(winequality.white)
cutpoint <- floor(nrows/3*2)
rand <- sample(1:nrows)
wine.train <- winequality.white[rand[1:cutpoint],]
wine.test <- winequality.white[rand[(cutpoint+1):nrows],]
model <- ksvm(highorlow ~., data= wine.train)
pred <- predict(model, wine.test)
predmatrix <- table(pred, wine.test$highorlow)
predmatrix
ksvmerror <- (predmatrix[[2]] + predmatrix[[3]])/(predmatrix[[1]] + predmatrix[[2]] + predmatrix[[3]] + predmatrix[[4]]) * 100
ksvmerror

#linear model of all the variables 
linearmodel <- lm(formula= quality ~ fixed.acidity + volatile.acidity + citric.acid + residual.sugar + chlorides + free.sulfur.dioxide + total.sulfur.dioxide + density + pH + sulphates + alcohol, data= winequality.white)
summary(linearmodel)


#graph the correlations
install.packages("corrplot")
library("corrplot")
correlations <- cor(winequality.white)
corrplot(correlations)

alcoholandsugar <- ggplot(mywinedata, aes(x= alcohol, y= residual.sugar, color= quality)) + geom_point() + scale_color_gradient(low= "red", high= "green")
alcoholandsugar

alcoholanddensity <- ggplot(winequality.white, aes(x= alcohol, y=density, color= quality)) + geom_point() + scale_color_gradient(low= "red", high= "green")
alcoholanddensity

sugaranddensity <- ggplot(winequality.white, aes(x= residual.sugar, y= density, color= quality)) + geom_point() + scale_color_gradient(low= "red", high= "green") + xlim(0,32) + ylim(0.985, 1.0105)
sugaranddensity

freesulfurandvolatile <- ggplot(winequality.white, aes(y= free.sulfur.dioxide, x= volatile.acidity, color= quality)) + geom_point() + scale_color_gradient(low= "red", high= "green") 
freesulfurandvolatile

alcohol <- ggplot(winequality.white, aes(x= quality, y= alcohol)) + geom_point()
alcohol

density <- ggplot(winequality.white, aes(x= quality, y= density)) + geom_point()  
density

volatile <- ggplot(winequality.white, aes(x= quality, y= volatile.acidity)) + geom_point()  
volatile

freesulfur <- ggplot(winequality.white, aes(x= quality, y= free.sulfur.dioxide)) + geom_point()  
freesulfur




