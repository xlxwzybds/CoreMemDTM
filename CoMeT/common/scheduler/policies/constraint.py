import numpy as np
from scipy.optimize import minimize



# Aim Function 
def Aim(x):
    return (x[0] - 1)**2 + (x[1] - 2)**2

# ConsPower
def ConsPower(x):
    return x[0]**2 + x[1]**2 - 5  # x[0]^2 + x[1]^2 <= 5

# package 
constraints = {'type': 'ineq', 'fun': lambda x: 5 - (x[0]**2 + x[1]**2)}  # g(x) >= 0

# bound 
Min_Freq = [0.1, 1]  # below
Max_Freq = [1  , 4]  # above 
bounds = [(Min_Freq[i], Max_Freq[i]) for i in range(len(Min_Freq))]

# initial point 
x0 = np.ones(2)  # initial point

# Optimization
result = minimize(Aim, x0, bounds=bounds, constraints=constraints, method='SLSQP')



