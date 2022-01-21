from numpy import *

def g(x,u,d,theta):
# auto-generated function from matlab

	x2 = x[1]
	x3 = x[2]
	theta2 = theta[1]
	theta7 = theta[6]
	theta13 = theta[12]
	theta14 = theta[13]
	theta15 = theta[14]
	out1 = (61*theta2**4*theta14*theta15*x2**2)/2000 
	out2 = (49*theta2**5*theta7*theta13*x2**2)/10000 
	out3 = (61*theta2**4*theta14*theta15*x3**2)/2000 
	out4 = (49*theta2**5*theta7*theta13*x3**2)/10000 

	return out1, out2, out3, out4
