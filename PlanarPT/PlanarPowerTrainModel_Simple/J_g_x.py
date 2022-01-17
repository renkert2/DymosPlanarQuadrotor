import math
import numpy as np

def J_g_x(x,a,u,d,theta):
# auto-generated function from matlab

	x1 = x[0]
	theta2 = theta[1]
	theta14 = theta[13]
	theta15 = theta[14]
	out1 = (61*theta2**4*theta14*theta15*x1)/500 

	return out1
