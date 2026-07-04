# Load and plot the built-in co2 dataset
data(co2)
plot(co2, 
     main = "Monthly Mauna Loa CO2 Concentration", 
     ylab = "CO2 (ppm)", 
     col = "blue", 
     lwd = 2)


# Step 1: Remove seasonality. 
# Monthly data has a frequency of 12, so we difference at lag=12.
co2_seasonal_diff <- diff(co2, lag = 1)
plot(co2_seasonal_diff, 
     main = "CO2 after Seasonal Differencing (lag=12)", 
     ylab = "Differenced CO2", 
     col = "darkgreen")

# Step 2: Remove remaining trend.
# The seasonal differencing might leave a slight trend, so we take a standard first difference (lag=1) of the already differenced data.
co2_stationary <- diff(co2_seasonal_diff, lag = 12)
plot(co2_stationary, 
     main = "CO2 after Seasonal (lag=12) and First (lag=1) Differencing", 
     ylab = "Fully Differenced CO2", 
     col = "purple")