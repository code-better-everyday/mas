# 1. Load the dataset into your global environment
data(UKgas)

# 2. Print the entire dataset to the console
print(UKgas)

# 3. Check the structure to confirm it is a Time Series ('ts') object
str(UKgas)

# 4. Plot the data to visually inspect the time series
plot(UKgas, main="UK Gas Consumption", ylab="Millions of Therms", col="blue")

UKgas[9]


X = c(5, 3, 7, 6)
Y = c(2, 4, 3, 1)

X[4:2]

sum(X[4:2] * Y[1:3])


# Set up the plotting area to show 3 rows and 1 column
par(mfrow = c(3, 1))

# Plot 1: Average Yearly Temperatures in New Haven
plot(nhtemp, 
     main = "nhtemp: Average Yearly Temperatures in New Haven", 
     ylab = "Temp (F)", 
     col = "steelblue", 
     lwd = 2)

# Plot 2: Monthly Accidental Deaths in the US
plot(USAccDeaths, 
     main = "USAccDeaths: Monthly Accidental Deaths in the US", 
     ylab = "Deaths", 
     col = "firebrick", 
     lwd = 2)

# Plot 3: Quarterly Australian Residents
plot(austres, 
     main = "austres: Quarterly Australian Population", 
     ylab = "Population (Thousands)", 
     col = "forestgreen", 
     lwd = 2)

# Reset the plotting layout back to default
par(mfrow = c(1, 1))



set.seed(1)
WN <- rnorm(200,0,3)
plot.ts(WN, xlab = '', ylab = '', main = 'Gaussian White Noise')

RW <- cumsum(WN)
plot.ts(RW, xlab = '', ylab = '', main = 'Random Walk')

