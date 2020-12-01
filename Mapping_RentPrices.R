# Drew Colbert

# This code here is used to create visuaizations that will go on a poster
# to show the differences in rent prices and what might be causing those differences.
# Below is code to explore some of the key areas of the data and view distributions, 
# as well as maps of the united states that show clear differences in the average rent price 
# at the state level as well as the county level. Some topics explored are the population of 
# various cities around the US and how that might alter the rent price and the area of water
# that each state contains as well. The thought is that areas with more people tend to have 
# increased rent prices, espeically in those really big cities, and waterfront property is 
# typically sought out, so theorhetically, the states with higher areas of water would have higher rent 
# prices

# install the required packages 
library(ggplot2)
library(RColorBrewer)
# install.packages("plotfunctions")
library("plotfunctions")
library(maps)
library(mapproj)
library(plotrix)

# read in the housing data
# kaggle_gross_rent.csv
# obtained from kaggle open datasets
# https://www.kaggle.com/goldenoakresearch/acs-gross-rent-us-statistics
file <- file.choose()
housing <- read.csv(file, 
                stringsAsFactors = FALSE)


# view the sturcture of the data
str(housing)
names(housing)
housing_clean <- housing[, c("State_Name", 
                             "State_ab", 
                             "County", 
                             "City", 
                             "Zip_Code",
                             "ALand",
                             "AWater",
                             "Lat",
                             "Lon",
                             "Mean",
                             "Median")]

colnames(housing_clean)[1] <- "state"


hist(housing$Median, 
     col = "orange",
     border = NA,
     xlab = "Median Rent Price",
     main = "Distribution of Rent Prices")

boxplot(housing$Median, 
        horizontal = TRUE,
        col = "lightpink1",
        xlab = "Median Rent Price",
        main = "Distribution of Rent Prices")


d <- density(log10(housing$AWater))
plot(d, 
     col = "royalblue2",
     main = "Distribution of the Area of Water",
     xlab = " ")

price_by_state <- tapply(housing$Median, list(housing$State_ab), median)
barplot(price_by_state[order(price_by_state)],
        col = c("blue", "springgreen3", "red"),
        horiz = TRUE,
        cex.names = .45,
        las = 1,
        xlab = "Median Rent Price",
        main = "Median Rent Price by State")


#########################################################################
# CREATING A MAP FOR RENT PRICES (STATE LEVEL)
#########################################################################

# get rid of alaska and hawaii from the dataset
zap <- which(housing_clean$state == "Alaska")
zap2 <- which(housing_clean$state == "Hawaii")
housing_clean <- housing_clean[-zap,]
housing_clean <- housing_clean[-zap2,]

# aggregate by state
df1 <- aggregate(housing_clean$Median, 
                 list(housing_clean$state), 
                 mean)

# change the names of the columns so they make more sense
colnames(df1) <- c("state", "rent")

# decide how many colors we want to use to represent the data
# max for "RdYlGn" is 11
# reverse so red is the higher numbers and green is lower
num.cols <- 11
col.vec <- rev(brewer.pal(num.cols, "RdYlGn"))

# rescale the values to be from 1-11, to match the number of colors
df1$index <- round(rescale(x = df1$rent, c(1, num.cols)), 0)
# map the colors to each row based on the rescaled values in the index
df1$color <- col.vec[df1$index]

# match the state names from the "map()" object to the state names in the df
# allows the state to be represented correctly in the map
m <- map(database = "state")
state.order <- match.map(database = "state",
                          regions = df1$state,
                          exact = FALSE,
                          warn = TRUE)

# make the actual map
# color gets mapped to the correct state because of "state.order"
map(database = "state",
    col = df1$color[state.order],
    fill = TRUE,
    resolution = 0,
    lty = 1,
    border = "black",
    bg = "white")
my.cols <- rep(rgb(1, 0, 1, alpha = 0.3), length(us.cities$name))

# map the populations of popular us cities over the map we created
# the populations are represented by the size of the circles
# the color is a light pink/purple
points(us.cities$long, us.cities$lat, col = my.cols,
       pch = 16,
       cex = rescale(us.cities$pop, c(.5, 7)))
gradientLegend(range(df1$rent), 
               col = rev(brewer.pal(num.cols, "RdYlGn")), 
               side = 3,
               dec = 0,
               tick.col = "black")


#########################################################################
# CREATE A MAP WITH JUST THE POPULATION DATA ON IT
#########################################################################
# the dataset "us.cities" is built into R
# create a blank white map of the US
map("state", fill = TRUE, col = "white", bg = "grey27")
my.cols <- rep(rgb(.7, .1, .7, .5), length(us.cities$name))
# add the points onto the blank map
points(us.cities$long, us.cities$lat, col = my.cols,
       pch = 16,
       cex = rescale(us.cities$pop, c(.5, 7)))


#########################################################################
# PLOT JUST CALIFORNIA
#########################################################################

# isolate just the data about california
cali <- housing_clean[which(housing_clean$state == "California"),]
# aggregate the counties by the average median rent price
df4 <- aggregate(cali$Median,
                 list(cali$County),
                 mean)
df4$rent <- round(df4$rent, 0)
# change the column names so its easier to understand
colnames(df4) <- c("county", "rent")

# run this to see how the names of the counties are formatted in R
m2 <- map("county")

# create a temporary variable to manipulate the formatting of the counties in the dataset we imported
tmp <- gsub(" County", "", df4$county)
tmp <- tolower(tmp)
for (i in 1:length(tmp)) {
     tmp[i] = paste("california,", tmp[i], sep = "")
}
# change the clean column names to be a part of the dataframe 
df4$county <- tmp

# rescale the values of the rent to be 1-11
# assign a color to each of those values
num.cols <- 11
col.vec <- rev(brewer.pal(num.cols, "RdYlGn"))
df4$index <- round(rescale(x = df4$rent, c(1, num.cols)), 0)
df4$color <- col.vec[df4$index]

# map all of the counties we have in our dataframe to the counties located in the map() function
county.order <- match.map(database = "county",
                         regions = df4$county,
                         exact = TRUE,
                         warn = TRUE)

# create the actual map
map(database = "county",
    region = "California",
    col = df4$color[county.order[157:213]],
    fill = TRUE,
    resolution = 0,
    lty = 1,
    border = "tan",
    bg = "grey27")
gradientLegend(valRange = df4$rent, 
               col = rev(brewer.pal(num.cols, "RdYlGn")),
               side = 3,
               dec = 0,
               n.seg = 1,
               pos.num = 3,
               length = .5)


#########################################################################
# MAPPING THE COUNTIES
#########################################################################
df5 <- aggregate(housing$Median,
                 list(housing$County, housing$state),
                 mean)
colnames(df5) <- c("county", "state", "rent")

# clean up the county names to match the names listed in the map() object
df5$county <- gsub(" County", "", df5$county)
df5$county <- gsub("^\\s*|A-z|a-z", "", df5$county)
df5$county <- tolower(df5$county)
df5$state <- tolower(df5$state)
state_list <- tolower(unique(housing$state))

# change the names of the counties to match
# example: "alabama,jefferson"
for (i in 1:dim(df5)[1]) {
    df5$county[i] = paste(df5$state[i], df5$county[i], sep = ",")
}


num.cols <- 11
col.vec <- rev(brewer.pal(num.cols, "RdYlGn"))
df5$index <- round(rescale(x = df5$rent, c(1, num.cols)), 0)
df5$color <- col.vec[df5$index]

county.order2 <- match.map(database = "county",
                          regions = df5$county,
                          exact = TRUE,
                          warn = TRUE)


map(database = "county",
    col = df5$color[county.order2],
    fill = TRUE,
    resolution = 0,
    lty = 1,
    border = "white",
    bg = "white")
my.cols <- rep(rgb(1, 0, 1, alpha = 0.3), length(us.cities$name))
gradientLegend(valRange = df4$rent, 
               col = rev(brewer.pal(num.cols, "RdYlGn")),
               side = 3,
               dec = 0,
               n.seg = 1,
               pos.num = 3,
               length = .25)


#########################################################################
# AWATER VS RENT
#########################################################################

# aggregate by the area of water first
df2 <- aggregate(housing_clean$AWater,
                 list(housing_clean$state),
                 mean)

# aggregate by the median rent price
df3 <- aggregate(housing_clean$Median,
                 list(housing_clean$state),
                 mean)

# change the column names
colnames(df2) <- c("state", "awater")

# add the rent column to the area of water df
df2$rent <- df3$x

# only look at the top 15 states with the highest rent price
df2_top15 <- df2[rev(order(df2$rent)),][1:15,]

# get rid of scientific notation
options(scipen = 999)

num.cols <- 5
col.vec <- brewer.pal(num.cols, "Blues")
df2_top15$index <- round(rescale(x = df2_top15$awater, c(1, num.cols)), 0)
df2_top15$color <- col.vec[df2_top15$index]

df2_top15 <- df2_top15[rev(order(df2_top15$rent)),]
df2_top15$state[1] <- "DC"

barplot(df2_top15$rent,
        col = df2_top15$color,
        ylab = "Median Rent Price",
        names.arg = df2_top15$state,
        cex.names = .7,
        las = 2)
gradientLegend(valRange = df2_top15$awater,
               col = col.vec,
               side = 3,
               dec = 0)

 











