from numpy import *

def J_f_x(x,a,u,d,theta):
# auto-generated function from matlab

	x1=x[0]
	J_r__MotorProp=theta[6]
	K_Q__Propeller=theta[7]
	
	out1 = -(2*K_Q__Propeller*x1)/J_r__MotorProp
	
	return out1
