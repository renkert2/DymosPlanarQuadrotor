from numpy import *

def J_h_x(x,a,u,d,theta):
# auto-generated function from matlab

	K_t__Motor=theta[9]
	
	out1 = -(2**(1/2)*3**(1/2)*K_t__Motor)/2
	out2 = -(2**(1/2)*3**(1/2)*K_t__Motor)/2
	
	return out1, out2
