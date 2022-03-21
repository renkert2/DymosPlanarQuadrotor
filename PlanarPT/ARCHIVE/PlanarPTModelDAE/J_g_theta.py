from numpy import *

def J_g_theta(x,a,u,d,theta):
# auto-generated function from matlab

	x2 = x[1]
	x3 = x[2]
	theta2 = theta[1]
	theta7 = theta[6]
	theta13 = theta[12]
	theta14 = theta[13]
	theta15 = theta[14]
	out1 = (61*theta2**3*theta14*theta15*x2**2)/500 
	out2 = (49*theta2**4*theta7*theta13*x2**2)/2000 
	out3 = (61*theta2**3*theta14*theta15*x3**2)/500 
	out4 = (49*theta2**4*theta7*theta13*x3**2)/2000 
	out5 = (49*theta2**5*theta13*x2**2)/10000 
	out6 = (49*theta2**5*theta13*x3**2)/10000 
	out7 = (49*theta2**5*theta7*x2**2)/10000 
	out8 = (49*theta2**5*theta7*x3**2)/10000 
	out9 = (61*theta2**4*theta15*x2**2)/2000 
	out10 = (61*theta2**4*theta15*x3**2)/2000 
	out11 = (61*theta2**4*theta14*x2**2)/2000 
	out12 = (61*theta2**4*theta14*x3**2)/2000 

	return out1, out2, out3, out4, out5, out6, out7, out8, out9, out10, out11, out12
