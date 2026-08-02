# Q2 
# Define the AR(2) coefficients: phi_1 = 0, phi_2 = 0.64
ar_coefs <- c(0, 0.64)

# Compute the theoretical ACF for the first 8 lags
# Note: R includes lag 0 as the first element, so we extract elements 2 through 9
theoretical_acf <- ARMAacf(ar = ar_coefs, ma = 0, lag.max = 8)[-1]
print("Theoretical ACF (Lags 1-8):")
print(theoretical_acf)

# Compute the theoretical PACF for the first 8 lags
theoretical_pacf <- ARMAacf(ar = ar_coefs, ma = 0, lag.max = 8, pacf = TRUE)
print("Theoretical PACF (Lags 1-8):")
print(theoretical_pacf)


# Q3 - a
set.seed(4)
# Model: X_t = 0.7 * X_{t-1} - 0.6 * X_{t-2} + W_t
ar_model <- list(ar = c(0.7, -0.6))
x_sim <- arima.sim(model = ar_model, n = 100, sd = 1)
sample_acvf <- acf(x_sim, type = "covariance", plot = FALSE)
acvf_lag0 <- sample_acvf$acf[1] # R stores lag 0 at index 1

sample_acf <- acf(x_sim, type = "correlation", plot = FALSE)
acf_first_few <- sample_acf$acf[1:4] 

# --- PRINT STATEMENTS ---
print(paste("Sample ACVF at lag 0:", round(acvf_lag0, 4)))
print("Sample ACF (Lags 0, 1, 2, 3):")
print(round(acf_first_few, 4))

# -- PART B -- MANUALLY DONE in handwritten notes, verify with R
r1 <- sample_acf$acf[2] # Lag 1
r2 <- sample_acf$acf[3] # Lag 2
phi1_hat <- (r1 * (1 - r2)) / (1 - r1^2)
phi2_hat <- (r2 - r1^2) / (1 - r1^2)
print(paste("Yule-Walker phi_1:", round(phi1_hat, 4)))
print(paste("Yule-Walker phi_2:", round(phi2_hat, 4)))

# --- PART C: Maximum Likelihood Estimators ---
# Fit using arima with method = "ML" and include.mean = FALSE
mle_fit <- arima(x_sim, order = c(2, 0, 0), include.mean = FALSE, method = "ML")
print("--- PART C: MLE Output ---")
print(mle_fit)
# Load the astsa library for the sarima function
library(astsa)

# --- PART D: Model Diagnostics ---
print("Generating sarima diagnostics for n = 100...")
sarima_fit <- sarima(x_sim, p = 2, d = 0, q = 0, no.constant = TRUE)
# 2. Test what happens with MORE timesteps (n = 1000) using the same seed
print("Generating sarima diagnostics for n = 1000...")
set.seed(4)
x_sim_large <- arima.sim(model = list(ar = c(0.7, -0.6)), n = 1000, sd = 1)
sarima_large_fit <- sarima(x_sim_large, p = 2, d = 0, q = 0, no.constant = TRUE)

# --- PART E: AIC and AICc Comparison ---
print("--- PART E: Information Criteria ---")

print("========== FIT AR(1) ==========")
sarima(x_sim, p = 1, d = 0, q = 0, no.constant = TRUE, details = FALSE)

print("========== FIT AR(2) ==========")
sarima(x_sim, p = 2, d = 0, q = 0, no.constant = TRUE, details = FALSE)

print("========== FIT AR(3) ==========")
sarima(x_sim, p = 3, d = 0, q = 0, no.constant = TRUE, details = FALSE)