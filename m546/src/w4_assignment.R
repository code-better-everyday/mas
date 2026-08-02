# The AR polynomial is 1 - 0.6z -0.37Z2 +0.21Z3
# Reversed order: ,0.21-0.37, -0.6, 1
reversed_coefs <- c(0.21,-0.37, -0.6, 1)
# Find inverse roots
inverse_roots <- polyroot(reversed_coefs)
print("Inverse Roots:")
print(inverse_roots)



c1 <- -0.7398332
c2 <- 1.651911
c3 <- 0.08792224
h <- 1:10

manual_acf <- c1*(0.5^h) + c2*(0.7^h) + c3*(-0.6)^h
builtin_acf <- ARMAacf(ar = c(0.6, 0.37, -0.21), lag.max = 10)[2:11] 

print("Manual Formula ACF:")
print(manual_acf)

print("ARMAacf Built-in ACF:")
print(unname(builtin_acf))


print("Do the two methods match exactly?")
print(all.equal(manual_acf, unname(builtin_acf), tolerance = 1e-4))



######################################################################
# QUESTION 3

reversed_coefs <- c(-0.08, -0.2, 1)
# Find inverse roots
inverse_roots <- polyroot(reversed_coefs)
print("Inverse Roots:")
print(inverse_roots)

# Check psi_1 for the ARMA(2,1) process
psi_vals <- ARMAtoMA(ar = c(0.2, 0.08), ma = 0.7, lag.max = 1)
print(paste("psi_1 from ARMAtoMA:", psi_vals[1]))















c1 <- 1.36467167
c2 <- -0.36467167
h <- 1:10
manual_acf <- c1*(0.4^h) + c2*(-0.2)^h
# AR 0.2 anbd 0.08 and MA is 0.7
builtin_acf <- ARMAacf(ar = c(0.2, 0.08), ma = 0.7, lag.max = 10)[2:11]

print("Manual Formula ACF:")
print(manual_acf)

print("ARMAacf Built-in ACF:")
print(unname(builtin_acf))

# 5. Compare for an exact match
print("Do the two methods match exactly?")
print(all.equal(manual_acf, unname(builtin_acf), tolerance = 1e-5))

