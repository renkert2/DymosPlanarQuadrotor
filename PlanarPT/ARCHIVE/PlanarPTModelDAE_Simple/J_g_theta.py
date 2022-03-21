from numpy import *

def J_g_theta(x,a,u,d,theta):
# auto-generated function from matlab

	x1 = x[0]
	theta2 = theta[1]
	theta14 = theta[13]
	theta15 = theta[14]
	out1 = (61*theta2**3*theta14*theta15*x1**2)/250 
	out2 = (61*theta2**4*theta15*x1**2)/1000 
	out3 = (61*theta2**4*theta14*x1**2)/1000 

	return out1, out2, out3
