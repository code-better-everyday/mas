################################################################################
## M546 Introduction to Time Series -- Course Summative Assessment            ##
## Analysis of the `chicken` dataset (astsa package)                          ##
##                                                                            ##
## Monthly whole-bird spot price, Georgia docks (US cents per pound),         ##
## Aug 2001 -- Jul 2016 (n = 180, monthly, frequency = 12).                   ##
##                                                                            ##
################################################################################

## ---------------------------------------------------------------------------
## 0. Setup
## ---------------------------------------------------------------------------
# install.packages("pacman")            
library(pacman)
p_load(astsa, fUnitRoots, forecast, tseries)

str(chicken)
start(chicken); end(chicken); frequency(chicken)   # 2001.8 (Aug 2001) -> 2016.5 (Jul 2016) - yearly

# --- Figure export helper --------------------------------------------------
plot_dir <- "C:/Users/abhis/git/mas/m546/src/final_plots"
dir.create(plot_dir, showWarnings = FALSE, recursive = TRUE)

savefig <- function(name, w = 1000, h = 650, res = 120) {
  dev.copy(png, filename = file.path(plot_dir, name),
           width = w, height = h, res = res)
  dev.off()
  invisible(name)
}


## ---------------------------------------------------------------------------
## 1. PRELIMINARY DISCUSSION -- initial plot                     
## ---------------------------------------------------------------------------
# Figure 1: raw series
par(mfrow = c(1, 1))
plot(chicken,
     main = "Monthly Price of Chicken (astsa)",
     ylab = "Price (Cents per Pound)",
     xlab = "Year",
     lwd  = 1.5,
     col  = "darkblue")
savefig("fig1_raw.png")

# Appears to be an upward trending, with some seasonality? variance doesn't seem to be a problem 
# a log/Box-Cox transform is likely not needed

## ---------------------------------------------------------------------------
## 2. PRELIMINARY TRANSFORMATIONS & DIFFERENCING ORDER        
## ---------------------------------------------------------------------------

BoxCox.lambda(chicken)    
# 1.68

# --- 2b. First-order (regular) differencing to remove the trend --------------
chicken_diff <- diff(chicken)          # lag-1 difference

# Figure 2: the first-differenced series 
plot(chicken_diff,
     main = "First-Order Difference of Chicken Prices",
     ylab = "Change in Price (Cents)",
     xlab = "Year",
     lwd  = 1.5,
     col  = "darkred")
abline(h = mean(chicken_diff), lty = 2)  # nonzero mean ~0.25 => an upward drift
savefig("fig2_diff.png")
mean(chicken_diff)                       # ~0.25 cents/month (this is the drift)

# --- 2c. Augmented Dickey-Fuller tests  ---
# Lag choice : (n - 1)^(1/3).
k <- floor((length(chicken) - 1)^(1/3))
k                                        # 5

# ADF on the RAW series. It trends, so allow a constant ('c') and const+trend
adfTest(chicken, type = "c",  lag = k)
adfTest(chicken, type = "ct", lag = k)

# ADF on the DIFFERENCED series. It has a nonzero mean (drift), so use 'c'
adfTest(chicken_diff, type = "c", lag = k)
adfTest(chicken_diff, type = "c", lag = 12)   # robustness at a longer lag


## ---------------------------------------------------------------------------
## 3. SAMPLE ACF & PACF                                       
## ---------------------------------------------------------------------------

# Figure 3: ACF of the RAW series -- very slow decay confirms differencing.
acf(chicken, lag.max = 48, main = "ACF of Raw Chicken Series")
savefig("fig3_acf_raw.png")

# Figure 4: ACF & PACF of the first-differenced series (the stationary series).
# lag.max = 48 so we can inspect the seasonal lags (12, 24, 36).
par(mfrow = c(1, 2))
acf(chicken_diff,  lag.max = 48, main = "ACF of Differenced Chicken")
pacf(chicken_diff, lag.max = 48, main = "PACF of Differenced Chicken")
savefig("fig_acf_pacf.png", w = 1100, h = 550)   # save the 2-panel figure
par(mfrow = c(1, 1))


## ---------------------------------------------------------------------------
## 4. FITTING THE MODEL -- auto.arima candidate search
## ---------------------------------------------------------------------------

# (a) Drift allowed -- auto.arima's unconstrained recommendation.
auto_drift <- auto.arima(chicken, trace = TRUE,
                         approximation = FALSE, stepwise = FALSE)
summary(auto_drift)
# Thorough-search winner: ARIMA(1,1,2)(1,0,0)[12], NO drift
#   AICc = 347.10, BIC = 362.69 -- best on both criteria.

# p values as well 
sarima(chicken, 1, 1, 2, 1, 0, 0, 12, no.constant = TRUE)

# (b) Drift-free search -- confirms the same winner and lets us weigh the
# appropriate drift-free models. auto.arima drops drift here because it is not
# statistically significant (drift p-value ~ 0.08-0.14 in the drift models) and
# AICc/BIC favor the drift-free fit.
auto_nodrift <- auto.arima(chicken, trace = TRUE,
                           approximation = FALSE, stepwise = FALSE,
                           allowdrift = FALSE)
summary(auto_nodrift)


## ---------------------------------------------------------------------------
## 5. TOP-CHOICE MODEL AND ALTERNATIVE -- raw output + equations
## ---------------------------------------------------------------------------


# Helper: print a coefficient table with std. errors, t-values and p-values
# for an Arima() fit (Arima's own printout omits p-values).
coef_table <- function(fit) {
  est <- coef(fit)
  se  <- sqrt(diag(vcov(fit)))
  tval <- est / se
  pval <- 2 * (1 - pnorm(abs(tval)))
  round(data.frame(estimate = est, std.err = se,
                   t.value = tval, p.value = pval), 4)
}

# ---- FINAL model: ARIMA(1,1,2)(1,0,0)[12], no drift ----
# This is the thorough-search winner (lowest AICc AND BIC). It uses a seasonal
# AR(1) term and no drift (drift was not statistically significant; see below).
fit_final <- Arima(chicken,
                   order    = c(1, 1, 2),
                   seasonal = list(order = c(1, 0, 0), period = 12),
                   include.drift = FALSE)
fit_final                 # coefficients, sigma^2, log-lik, AIC, AICc, BIC
coef_table(fit_final)     # p-values -- expect all four terms significant


# lets do a quick search for an alternate model, see it if differs from original thorough search
auto.arima(chicken)

# ---- ALTERNATIVE model: ARIMA(2,1,1)(0,0,1)[12] with drift ----
fit_alt <- Arima(chicken,
                 order    = c(2, 1, 1),
                 seasonal = list(order = c(0, 0, 1), period = 12),
                 include.drift = TRUE)
fit_alt
coef_table(fit_alt)


# (3,1,0)(0,0,1)[12] +drift : best of the seasonal-MA/drift family (AICc 350.68).
fit_c1 <- Arima(chicken, order = c(3,1,0),
                seasonal = list(order = c(0,0,1), period = 12),
                include.drift = TRUE)
fit_c1
# (2,1,0)(0,0,1)[12] no drift : parsimonious, PACF-motivated (AR(2) + seasonal MA).
fit_c2 <- Arima(chicken, order = c(2,1,0),
                seasonal = list(order = c(0,0,1), period = 12),
                include.drift = FALSE)
fit_c2
# Drift-free counterpart of the alternative, for the drift vs no-drift plot.
fit_alt_nd <- Arima(chicken, order = c(2,1,1),
                    seasonal = list(order = c(0,0,1), period = 12),
                    include.drift = FALSE)

# ---- AIC / AICc / BIC comparison across candidates ----

model_compare <- data.frame(
  model = c("ARIMA(1,1,2)(1,0,0)[12] no drift  [FINAL]",
            "ARIMA(2,1,1)(0,0,1)[12] +drift    [ALT]",
            "ARIMA(3,1,0)(0,0,1)[12] +drift",
            "ARIMA(2,1,0)(0,0,1)[12] no drift"),
  AIC  = c(fit_final$aic, fit_alt$aic, fit_c1$aic, fit_c2$aic),
  AICc = c(fit_final$aicc, fit_alt$aicc, fit_c1$aicc, fit_c2$aicc),
  BIC  = c(fit_final$bic, fit_alt$bic, fit_c1$bic, fit_c2$bic))
model_compare[order(model_compare$AICc), ]



## ---------------------------------------------------------------------------
## 6. MODEL DIAGNOSTICS                                       
## ---------------------------------------------------------------------------

# Figure 5: diagnostics for the FINAL model, ARIMA(1,1,2)(1,0,0)[12] no drift.
diag_final <- sarima(chicken, 1, 1, 2, 1, 0, 0, 12, no.constant = TRUE)
savefig("fig_diag_final.png", w = 900, h = 1000)   # tall: 4 stacked panels
diag_final$ICs         # sarima's per-observation AIC/AICc/BIC (do not mix scales)

# Figure 6: diagnostics for the ALTERNATIVE, ARIMA(2,1,1)(0,0,1)[12] + drift.
# (d + D = 1, so sarima includes the constant = drift automatically.)
diag_alt <- sarima(chicken, 2, 1, 1, 0, 0, 1, 12)
savefig("fig_diag_alt.png", w = 900, h = 1000)
diag_alt$ICs


## ---------------------------------------------------------------------------
## 7. FORECASTING               
## ---------------------------------------------------------------------------
# Forecast 24 months (2 years) beyond Jul 2016, with 80% and 95% intervals.
h <- 24
fc_final <- forecast(fit_final, h = h)     # FINAL model (no drift)
fc_final                                   # numeric point forecasts + CIs

# Figure 8: forecast from the FINAL model.
par(mfrow = c(1, 1))
plot(fc_final,
     main = "ARIMA(1,1,2)(1,0,0)[12] -- 24-Month Forecast",
     ylab = "Price (Cents per Pound)", xlab = "Year")
savefig("fig_forecast.png")

# Zoomed view of just the forecast region (optional figure):
plot(fc_final, xlim = c(2013, 2018.5),
     main = "Forecast (zoomed)", ylab = "Price (Cents per Pound)", xlab = "Year")
savefig("fig_forecast_zoom.png")

# Figure 9 : final (no-drift) vs alternative (with-drift) forecasts,

fc_alt <- forecast(fit_alt, h = h)         # ALTERNATIVE model (with drift)
par(mfrow = c(1, 2))
plot(fc_final, xlim = c(2013, 2018.5),
     main = "Final: (1,1,2)(1,0,0), no drift", ylab = "Cents/lb", xlab = "Year")
plot(fc_alt,   xlim = c(2013, 2018.5),
     main = "Alt: (2,1,1)(0,0,1), with drift", ylab = "Cents/lb", xlab = "Year")
savefig("fig_forecast_compare.png", w = 1100, h = 550)
par(mfrow = c(1, 1))



# --- sarima.for() cross-check (astsa's own forecaster) ---------------------
par(mfrow = c(1, 1))
sarima.for(chicken, n.ahead = h, 1, 1, 2, 1, 0, 0, 12, no.constant = TRUE)
title(main = "sarima.for() cross-check -- FINAL model")
savefig("fig_sarimafor_final.png")
# Alternative (with drift): d + D = 1 so the constant is included automatically.
sarima.for(chicken, n.ahead = h, 2, 1, 1, 0, 0, 1, 12)
title(main = "sarima.for() cross-check -- ALT model")
savefig("fig_sarimafor_alt.png")
################################################################################
## End of analysis script.
################################################################################
