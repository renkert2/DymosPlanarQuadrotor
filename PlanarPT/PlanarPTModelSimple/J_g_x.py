from numpy import *

def J_g_x(x,a,u,d,theta):
# auto-generated function from matlab

	x1=x[0]
	K_T__Propeller=theta[8]
	
	out1 = 4*K_T__Propeller*x1
	
	return out1
