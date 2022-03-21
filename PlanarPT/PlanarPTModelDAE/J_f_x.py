from numpy import *

def J_f_x(x,a,u,d,theta):
# auto-generated function from matlab

	x2=x[1]
	x3=x[2]
	J_r__MotorProp=theta[6]
	K_Q__Propeller=theta[7]
	
	out1 = -(2*K_Q__Propeller*x2)/J_r__MotorProp
	out2 = -(2*K_Q__Propeller*x3)/J_r__MotorProp
	
	return out1, out2
