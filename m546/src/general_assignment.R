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





# Roots 

p<- c(1,-1.8,1.05,-0.196)
polyroot(p)
1/polyroot(p)


p_rev <-c(-0.196,1.05,-1.8,1)
polyroot(p_rev)


# revwee order used for roots - revrse 1 in END
p_rev <-c(+0.147, +0.07, -1.1, 1)
polyroot(p_rev)
 #AR equation says phi(z)  = (1+0.3z)(1-0.7z)(1-.07z)

p_rev <-c(-0.84, 0.5, 1)
polyroot(p_rev)
# ma eqyuati theta(z) = (1-0.7z)(1 + 1.2z)



# practise assignment - remember ulta root 1 in end that goe sto Xt 
p_rev <-c(   0.57 ,-2.716, 4.7, -3.6, 1)
polyroot(p_rev)


p_rev <-c(  0.56, -10.5, 1)
polyroot(p_rev)


p_rev <-c( 0.3, -1.1, 1)
polyroot(p_rev)

polyroot(c(0.3, -1.1, 1))


polyroot(c(0.98, -1.4, 1))

# these are all on same sdie that is xt +1.3xt-1 +0.35xt-2 = wt
polyroot(c(0.36, 1.3, 1))
# equal (1+0.4z)(1+0.9z) less than one so causal




# Reversed order: 0.79, -1.1, 1
reversed_coefs <- c(0.79, -1.1, 1)
# Find inverse roots
inverse_roots <- polyroot(reversed_coefs)
print("Inverse Roots:")
print(inverse_roots)
# Magnitude of the inverse roots 
magnitudes <- Mod(inverse_roots)
print("Magnitudes:")
print(magnitudes)

