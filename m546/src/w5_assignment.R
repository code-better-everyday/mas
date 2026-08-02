# 1. Set seed for reproducibility
set.seed(42)

# 2. Define the number of simulations
num_sims <- 10000

# 3. Helper function to simulate ARMA(2,1) and extract ACF at Lag 3
get_lag3_acf <- function(n_length) {
  x <- arima.sim(model = list(ar = c(0.2, 0.08), ma = 0.7), n = n_length, sd = 1)
  sample_acf <- acf(x, lag.max = 3, plot = FALSE)
  return(sample_acf$acf[4]) 
}

# 4. Run the simulations
acf_100 <- replicate(num_sims, get_lag3_acf(100))
acf_1000 <- replicate(num_sims, get_lag3_acf(1000))
acf_10000 <- replicate(num_sims, get_lag3_acf(10000))

# 5. PREPARE THE UNIVERSAL SCALE AND BREAKS
all_data <- c(acf_100, acf_1000, acf_10000)
universal_breaks <- seq(min(all_data) - 0.02, max(all_data) + 0.02, length.out = 60)
universal_xlim <- c(min(all_data), max(all_data))

h1 <- hist(acf_100, breaks = universal_breaks, plot = FALSE)
h2 <- hist(acf_1000, breaks = universal_breaks, plot = FALSE)
h3 <- hist(acf_10000, breaks = universal_breaks, plot = FALSE)
universal_ylim <- c(0, max(c(h1$counts, h2$counts, h3$counts)) * 1.2)

# compute theoretical value for the blue line - remember index 4 is lag 3 as lag 0 is index 1
theoretical_lag3 <- unname(ARMAacf(ar = c(0.2, 0.08), ma = 0.7, lag.max = 3)[4])

# 6. PLOT THE HISTOGRAMS
par(mfrow = c(1, 3))

# Plot n = 100
hist(acf_100, 
     breaks = universal_breaks, 
     xlim = universal_xlim, 
     ylim = universal_ylim, 
     main = "10000 simulations of rho.hat(3)\nTime Series of Length\n100", 
     xlab = "", 
     col = "gray95")
abline(v = theoretical_lag3, col = "blue", lwd = 1)

# Plot n = 1000
hist(acf_1000, 
     breaks = universal_breaks, 
     xlim = universal_xlim, 
     ylim = universal_ylim, 
     main = "10000 simulations of rho.hat(3)\nTime Series of Length\n1000", 
     xlab = "", 
     col = "gray95")
abline(v = theoretical_lag3, col = "blue", lwd = 1)

# Plot n = 10000
hist(acf_10000, 
     breaks = universal_breaks, 
     xlim = universal_xlim, 
     ylim = universal_ylim, 
     main = "10000 simulations of rho.hat(3)\nTime Series of Length\n10000", 
     xlab = "", 
     col = "gray95")
abline(v = theoretical_lag3, col = "blue", lwd = 1)

# Reset layout
par(mfrow = c(1, 1))