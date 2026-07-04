# The AR polynomial is 1 - 0.8z + 0.2z^2
# Reversed order: 0.2, -0.8, 1
reversed_coefs <- c(0.2, -0.8, 1)
# Find inverse roots
inverse_roots <- polyroot(reversed_coefs)
print("Inverse Roots:")
print(inverse_roots)
# Magnitude of the inverse roots 
magnitudes <- Mod(inverse_roots)
print("Magnitudes:")
print(magnitudes)



# Solve the linear system for c1 and c2
A <- matrix(c(1, 0.4+0.2i, 1, 0.4-0.2i), 2, 2)
h_vec <- c(1, 2/3)
c_vals <- solve(A, h_vec)
print("c_values")
print(c_vals)


# Extract polar coordinates
c1 <- c_vals[1]
r1_inv <- 0.4 + 0.2i

alpha <- Mod(c1)
theta <- Arg(c1)     
beta <- Mod(r1_inv)  
phi <- Arg(r1_inv)   
print("Alpha, Theta, Beta, Phi:")
print(c(alpha, theta, beta, phi))

# Compute the ACF using the derived formula
manual_acf <- 2 * alpha * (beta^h) * cos(phi * h + theta)
print("manual_acf")
manual_acf

#ACF using the built-in ARMAacf function

# Lag 0 is dropped by subsetting [2:11]
builtin_acf <- ARMAacf(ar = c(0.8, -0.2), lag.max = 10)[2:11] 
print("Using R ACF is")
builtin_acf


# 4. Print results
print("Manual Formula ACF:")
print(manual_acf)

print("ARMAacf Built-in ACF:")
print(unname(builtin_acf))

# 5. Compare for an exact match
print("Do the two methods match exactly?")
print(all.equal(manual_acf, unname(builtin_acf)))



plot(builtin_acf, type = 'h', xlim = c(0,7), ylim = c(-1,1), xlab = '')
abline(h = 0)
points(0, 1, type = 'h')