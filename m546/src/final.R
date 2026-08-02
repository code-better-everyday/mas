# Load the required packages
library(astsa)
library(tseries) # We will need this later for the Dickey-Fuller test

# 1. Generate the initial plot for the chicken dataset
# The dataset tracks the monthly price of a pound of chicken
plot(chicken, 
     main = "Monthly Price of Chicken (astsa)", 
     ylab = "Price (Cents per Pound)", 
     xlab = "Year",
     lwd = 1.5,
     col = "darkblue")


# Make sure the tseries package is loaded for the adf.test() function
library(tseries)

# --- 1. Formal Augmented Dickey-Fuller Test on raw data ---
# Null Hypothesis (H0): The time series has a unit root (is non-stationary)
# Alternative Hypothesis (HA): The time series is stationary
print("--- ADF Test on Raw Data ---")
adf_raw <- adf.test(chicken)
print(adf_raw)

# --- 2. Apply first-order differencing ---
chicken_diff <- diff(chicken)

# --- 3. Plot the differenced data ---
plot(chicken_diff, 
     main = "First-Order Difference of Chicken Prices", 
     ylab = "Change in Price (Cents)", 
     xlab = "Year",
     lwd = 1.5,
     col = "darkred")

# --- 4. Formal Augmented Dickey-Fuller Test on differenced data ---
print("--- ADF Test on Differenced Data ---")
adf_diff <- adf.test(chicken_diff)
print(adf_diff)

# --- 5. ACF and PACF plots of the differenced data ---
par(mfrow = c(1, 2)) 
acf(chicken_diff, main = "ACF of Differenced Chicken")
pacf(chicken_diff, main = "PACF of Differenced Chicken")
par(mfrow = c(1, 1))



# Load the forecast package for auto.arima
library(forecast)

# --- 6. Candidate Model Search ---
# We run this on the RAW data, because auto.arima can handle the differencing internally.
# We set trace = TRUE to see the list of models it tries.
print("--- Auto ARIMA Trace ---")
auto_fit <- auto.arima(chicken, trace = TRUE, seasonal = TRUE)

# Print the top recommended model
print("--- Best Model Suggested by auto.arima ---")
summary(auto_fit)