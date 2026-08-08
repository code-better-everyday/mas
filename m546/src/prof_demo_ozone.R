################################################################################
## Live Session 3 Code                                                       ###
## Analysis of dataset "ozone.dat" from tsdl                                 ###
## Available at http://robjhyndman.com/tsdldata/monthly/ozone.dat            ###
##                                                                           ###
## Note: This is intended to help you with your Course Summative Assessment. ###
## However, you will generally need to provide more detail in your write-up  ###
## than is given in the comments below. Furthermore, some of the code below  ###
## is not explained thoroughly in the comments.  Most of it will be          ###
## discussed during Live Session 3.                                          ###
##                                                                           ###
## NOTE: This is the PROFESSOR'S reference demo (ozone dataset), saved into   ###
## the repo for reference only. Our actual assignment uses the `chicken`      ###
## dataset -- see final.R.                                                    ###
################################################################################

install.packages("pacman")
library(pacman)
p_load(astsa, fUnitRoots, forecast)

?scan

## Grab the dataset from online
ozone.data <- scan("http://robjhyndman.com/tsdldata/monthly/ozone.dat",skip=1)
ozone.data
ozone.ts <- ts(ozone.data, start = c(1955), frequency = 12)
ozone.ts


## Or alternatively, copy-paste it into a .txt (or .csv) file
## and grab it from there.
ozone.data.alt <- scan("ozone.txt", skip = 1)
ozone.ts.alt <- ts(ozone.data.alt, start = 1955, frequency = 12)
ozone.ts.alt

# Don't forget to format properly!
# Here's an improperly formatted call, which will end
# in *January* 1972:
 ozone.ts <- ts(ozone.data, start = 1955, end = c(1972, 12), frequency = 12)
 ozone.ts
#

par(mfrow = c(1,1))
plot(ozone.ts)
plot(ozone.ts, xlim = c(1960, 1965))


## Looks like no preliminary transformations (e.g., log-transformation or
## Box-Cox transformation) are needed here.

# Perform a lag-12 difference to see if it removes the periodic structure
X<-diff(ozone.ts, lag = 12)
X
plot(X)
plot(X, xlim = c(1960, 1965))
mean(X)
abline(h = 0)

# We fit a SARIMA model to the dataset.  We anticipate using a model of the form
# SARIMA(p,d,q) x (P,1,Q)[12].
# To decide whether to use 0 or 1 for d, we run Augmented Dickey-Fuller
# To make an educated guess for p,q,P,Q, we look at plots of the sample ACF
# and sample PACF of the dataset we get after we're done differencing.



# Run augmented Dickey--Fuller Test on seasonally differenced data.
# ADF test applied to dataset X tells you whether to difference X.

(length(X)-1)^(1/3)
adfTest(X, 'nc', lag = 5)
adfTest(X, 'nc', lag = 12)
# Small p-value --> reject null hypothesis/do not difference again


adfTest(ozone.ts, 'c', lag = 5)  # See video for explanation. Make sure
adfTest(ozone.ts, 'c', lag = 12) # that you're applying the test to the
                                 # intended dataset!


# Look at sample ACF and sample PACF of the lag-12 differenced data
par(mfrow = c(1,2))
acf(X, lag.max = 48)
pacf(X, lag.max = 48)

# ACF of undifferenced data decays very slowly--a confirmation that some
# kind of differencing is almost certainly warranted
acf(ozone.ts, lag.max = 100)




# Remember:
# Pure MA model --> sample ACF should almost cut off after a few lags
# Pure AR model --> sample PACF should almost cut off after a few lags


# TL guess: P=0 (seasonal AR), Q = 1 (seasonal MA component),
#           p = ?, q = ?  Probably both at least 1, but unclear


# Let's see what auto.arima gives us.
?auto.arima
auto.arima(ozone.ts, trace = TRUE, approximation = FALSE)
## It picks ARIMA(1,0,2)(0,1,1)[12] with drift

?Arima
Arima(ozone.ts, order = c(1,0,2), seasonal = c(0,1,1), include.drift = TRUE)

## If you want to avoid working with models with drift, use this:
auto.arima(ozone.ts, trace = TRUE, approximation = FALSE, allowdrift = FALSE)
## (1 - 0.9790 B)(1 - B^{12}) X_t = (1 - 0.6327B - 0.2032 B^2)(1 - 0.7398 B^{12})W_t
## Wt ~ W(0,0.6797)

## In your own analysis (and in particular on your Course Summative Assessment),
## you'll need to consider some alternative models.
## You are recommended to look through the models auto.arima has "traced" through
## for this purpose, and consider models with AIC/AICc values that are nearly
## as small as the one auto.arima chose.  We skip this step today.


## Look at model diagnostics using sarima
ozone.model1<-sarima(ozone.ts, 1,0,2,0,1,1, 12)


# Note: Without "approximation = FALSE", routine picks
# ARIMA(3,0,3)(2,1,2)[12], which has many more parameters.  Let's compare the
# model diagnostics (and AIC/AICc values) against our earlier model.
# We are also interested to see if we can remove some of the parameters in
# the ARIMA(3,0,3)(2,1,2)[12] fit to get a more parsimonious model.
auto.arima(ozone.ts, trace = TRUE, allowdrift = FALSE)


sarima(ozone.ts, 3,0,3,2,1,2,12)

# "Fix" some of the parameters to be equal to zero.
sarima(ozone.ts, 3,0,3,2,1,1,12)
sarima(ozone.ts, 3,0,3,1,1,1,12)
sarima(ozone.ts, 3,0,3,0,1,1,12)
sarima(ozone.ts, 3,0,3,1,1,1,12, fixed = c(0, NA, NA, NA, NA, NA, NA, NA))
sarima(ozone.ts, 3,0,2,1,1,1,12, fixed = c(0, NA, NA, NA, NA, NA, NA))


sarima(ozone.ts, 3,0,3,2,1,2,12, fixed = c(0, NA, NA, NA, NA, NA, NA, NA, NA, NA))
sarima(ozone.ts, 3,0,3,2,1,1,12, fixed = c(0, NA, NA, NA, NA, NA, NA, NA, NA))
sarima(ozone.ts, 3,0,3,1,1,1,12, fixed = c(0, NA, NA, NA, NA, NA, NA, NA))
sarima(ozone.ts, 3,0,3,0,1,1,12, fixed = c(0, NA, NA, NA, NA, NA, NA))
sarima(ozone.ts, 3,0,3,0,1,1,12, fixed = c(0, 0, NA, NA, NA, NA, NA))

# AIC is a tiny bit lower here, but Ljung-Box values are bad,
# and there's still one more parameter than our current
# favorite.


sarima(ozone.ts, 3,0,3,0,1,1,12)
test<-sarima(ozone.ts, 3,0,3,0,1,1,12, fixed = c(0, NA, NA, NA, 0, NA, NA))

# This last model is another contender; it has AICC close to
# our current favorite; however, there is 1 more parameter,
# so we don't select it.


# We accept the SARIMA(1,0,2)(0,1,1)[12] model.  Let's store it for use in
# forecasts
ozone.fit <- arima(ozone.ts, order = c(1,0,2),
                   seasonal = list(order = c(0,1,1), period = 12))

# Another set of diagnostics
checkresiduals(ozone.fit)

###################################################################
## Let's forecast!

ozone.forecast <- forecast(ozone.fit, h = 36)
ozone.forecast

par(mfrow = c(1,1))
plot(ozone.forecast)



## Just some different ways of looking at the forecast.
plot(ozone.forecast, xlim = c(1965, 1976))
plot(ozone.forecast, xlim = c(1973, 1976))


## Numerical values of the point forecasts and confidence intervals
ozone.forecast

###################################################################
## Exponential Smoothing Fit (Not covered during the live session)

ozone.fit.HW <- HoltWinters(ozone.ts)
ozone.fit.HW
# Output consists of the parameters for the model
# alpha = smoothing parameter for level
# beta = smoothing parameter for trend
# gamma = smoothing parameter for seasonality
# (See Module 8, Lesson 2 for the relevant equations, both the "original"
# system and the state-space representation.)
# a  = final value of level
# b  = final value of trend
# sj = final value of seasonal component j

plot(ozone.fit.HW)
checkresiduals(ozone.fit.HW)

# Visual inspection of the fit seems okay; diagnostics are acceptable
# (though Ljung-Box test p-value is not much higher than 0.1).

ozone.forecast.HW <- forecast(ozone.fit.HW, h = 36)


par(mfrow = c(1,1))
plot(ozone.forecast.HW)
plot(ozone.forecast.HW, xlim = c(1965, 1976))
plot(ozone.forecast.HW, xlim = c(1971, 1975))


# Just out of curiosity, compare the ARIMA and exponential smoothing forecasts:
par(mfrow = c(1,2))
plot(ozone.forecast, xlim = c(1965, 1976))
plot(ozone.forecast.HW, xlim = c(1965, 1976))


#
ozone.fit.HW$coefficients
a<-as.numeric(ozone.fit.HW$coefficients[1])
a
b<-as.numeric(ozone.fit.HW$coefficients[2])
b
s2<-as.numeric(ozone.fit.HW$coefficients[4])
s2
s5<-as.numeric(ozone.fit.HW$coefficients[7])
s5

# Point forecast equation (Module 8, Lesson 2, p. 5, bottom) is
# x^t_{t+m} = l_t + m*b_t + s_{t+m - T(k+1)}
# ozone.ts has December 1972 as final observation.
# To get a forecast for May 1973, we set m = 5 (and use s5)
# To get a forecast for February 1974, we set m = 14 (and use s2)

a + 5*b + s5
a + 14*b + s2

ozone.forecast.HW
