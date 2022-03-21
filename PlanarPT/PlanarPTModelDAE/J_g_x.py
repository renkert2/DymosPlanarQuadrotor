from numpy import *

def J_g_x(x,a,u,d,theta):
# auto-generated function from matlab

	x2=x[1]
	x3=x[2]
	K_Q__Propeller=theta[7]
	K_T__Propeller=theta[8]
	
	out1 = 2*K_T__Propeller*x2
	out2 = 2*K_Q__Propeller*x2
	out3 = 2*K_T__Propeller*x3
	out4 = 2*K_Q__Propeller*x3
	
	return out1, out2, out3, out4
