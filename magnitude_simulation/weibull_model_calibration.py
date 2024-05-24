import numpy as np
from scipy.special import gamma
# Coefficient of Variation squared (CV^2)
CV2 = 0.030309
# Calculate shape parameter (k)
k = np.sqrt(np.log(1 + CV2))
# Calculate scale parameter (λ)
mean =  3.416374
λ = mean / gamma(1 + 1/k)
# Print the estimated parameters
print("Estimated shape parameter (k):", k)
print("Estimated scale parameter (λ):", λ)