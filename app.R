# writing a program to explore different stocks with potential returns 

library(quantmod)
library(PerformanceAnalytics)
library(dygraphs)
# install.packages("shiny", dependencies = TRUE)
library(shiny)
# install.packages("htmltools")
library(highcharter)
# install.packages("prophet")
library(prophet)
# install.packages("shinythemes")
library(shinythemes)
# install.packages("DT")
library(DT)
library(rsconnect)

# when adding objects to the shiny app (whether it inputs OR outputs)...
# you add it to the fluidPage function (can look up inputs and outputs on google)
ui <- fluidPage(
    
    # theme changes the style of the app
    theme = shinytheme("united"),
    
    # add a title to the app
    titlePanel("Explore a Stock"),
    
    # creates a sidebar where I can place all of the user inputs 
    sidebarPanel(
        
        textInput(inputId = "stock_name", label = "Insert a stock symbol"),
        
        dateRangeInput(inputId = "date_range", label = "Insert a Date Range"),
        
        sliderInput(inputId = "initial", min = 1, max = 5000, value = 100, step = 1, label = "Enter Initial Investment Amount"),
        
        submitButton("Update"),
        
        # creates line breaks in the sidebar (this is HTML language)
        br(),
        br(),
        br(),
        
        # used to display the beta value
        textOutput(outputId = "beta"),
        
        # used to display the expected return after one month given a certain initial investment
        textOutput(outputId = "expected_return")
    ),
    
    mainPanel(
        
        tabsetPanel(
            # creates a collection of tabs that can display different information
            
            tabPanel("Adj Stock Price", highchartOutput(outputId = "raw_adj_price")),
            tabPanel("Monthly Returns", highchartOutput(outputId = "monthly_returns")),
            
            # used to plot the prophet prediction
            tabPanel("Predicted Adj Price",
                     # im using fluidRow to add an additional piece of information to this tab and only this tab
                     fluidRow(column(6, textOutput(outputId = "runtime_message"))),
                     fluidRow(column(10, plotOutput(outputId = "prophet"))),
                     fluidRow(column(7, textOutput(outputId = "prophet_details"))))
        ),
        
        DT::dataTableOutput(outputId = "raw_values")
    )
)

server <- function(input, output) {
    # the server is where the actual plots get constructed
    # the name we save the object to must match the name we gave it in the ui
    # this is all normal code to create these plots, but they must be inside of a render function
    # the render function is what updates the charts after the user changes a value
    
    # req() just means that a user input must be set before this code runs
    # this gets rid of the error messages that would occur when you first opened up the app
    
    # creating an hchart of the monthly returns for a given stock
    output$raw_adj_price <- renderHighchart({
        req(input$stock_name)
        req(input$date_range)
        stock <- toupper(input$stock_name)
        getSymbols(stock, from = input$date_range[1], to = input$date_range[2], warnings = FALSE)
        adj_price <- get(noquote(stock))[,6]
        hchart(adj_price,
               name = "Adj Price",
               color = "orangered",
               type = "area")
    })
    
    output$monthly_returns <- renderHighchart({
        req(input$stock_name)
        req(input$date_range)
        stock <- toupper(input$stock_name)
        getSymbols(stock, from = input$date_range[1], to = input$date_range[2], warnings = FALSE)
        monthly_returns <- monthlyReturn(get(noquote(stock))[,6])
        hchart(round(monthly_returns, 4) * 100, 
               name = "Return Value (%)", 
               color = "orangered")
    })
    
    # prints the beta value of the stock
    output$beta <- renderText({
        req(input$stock_name)
        req(input$date_range)
        stock <- toupper(input$stock_name)
        getSymbols(stock, from = input$date_range[1], to = input$date_range[2], warnings = FALSE)
        getSymbols("^GSPC", from = input$date_range[1], to = input$date_range[2], warnings = FALSE)
        getSymbols("DGS3MO", src = "FRED")
        sp_monthly <- monthlyReturn(GSPC)
        bills_monthly <- DGS3MO/1200
        stock_excess <- (monthlyReturn(get(noquote(stock))[,6])) - bills_monthly
        sp_excess <- sp_monthly - bills_monthly
        model <- lm(stock_excess ~ sp_excess)
        paste("Beta value:", round(model$coefficients[2], 3), sep = " ")
    })
    
    # prints the expected return after one month based on the investment given on the slider
    output$expected_return <- renderText({
        req(input$stock_name)
        req(input$date_range)
        stock <- toupper(input$stock_name)
        initial_investment <- input$initial
        getSymbols(stock, from = input$date_range[1], to = input$date_range[2], warnings = FALSE)
        monthly_returns <- (monthlyReturn(get(noquote(stock))[,6]))
        expected_return <- initial_investment * mean(monthly_returns)
        paste("Expected Return Per Month:", round(expected_return, 2), sep = " ")
    })
    
    output$runtime_message <- renderText({
        "*Predictions take a few seconds to load"
    })
    
    # predicts the future price of the stock
    output$prophet <- renderPlot({
        req(input$stock_name)
        req(input$date_range)
        stock <- toupper(input$stock_name)
        initial_investment <- input$initial
        getSymbols(stock, from = input$date_range[1], to = input$date_range[2], warnings = FALSE)
        df <- data.frame(ds = index(get(noquote(stock))), y = as.numeric(get(noquote(stock))[,6]))
        prophetpred <- prophet(df, daily.seasonality = TRUE)
        future <- make_future_dataframe(prophetpred, periods = 365)
        forecast <- predict(prophetpred, future)
        plot(prophetpred, forecast, xlabel = "Time", ylabel = "Adjusted Stock Price", figsize = c(25,35))
    })
    
    output$prophet_details <- renderText({
        req(input$stock_name)
        req(input$date_range)
        stock <- toupper(input$stock_name)
        initial_investment <- input$initial
        getSymbols(stock, from = input$date_range[1], to = input$date_range[2], warnings = FALSE)
        df <- data.frame(ds = index(get(noquote(stock))), y = as.numeric(get(noquote(stock))[,6]))
        prophetpred <- prophet(df, daily.seasonality = TRUE)
        future <- make_future_dataframe(prophetpred, periods = 365)
        forecast <- predict(prophetpred, future)
        paste("Max Predicted Stock Price Over 1 Year: ", 
              round(max(forecast$yhat[match(forecast$yhat[dim(forecast)[1] - 365], forecast$yhat):match(forecast$yhat[dim(forecast)[1]], forecast$yhat)]), 2))
    })
    
    output$raw_values <- DT::renderDataTable({
        req(input$stock_name)
        req(input$date_range)
        stock <- toupper(input$stock_name)
        getSymbols(stock, from = input$date_range[1], to = input$date_range[2], warnings = FALSE)
        stock_df <- data.frame(get(stock))
        datatable(stock_df, 
                  rownames = TRUE,
                  options = list(lengthMenu = list(c(5,10,30), c("5","10","30")), pageLength = 10)) 
    })
}
shinyApp(ui = ui, server = server)
















