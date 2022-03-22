from numpy import *

def J_f_theta(x,a,u,d,theta):
# auto-generated function from matlab

	x1=x[0]
	a5=a[4]
	J_r__MotorProp=theta[6]
	K_Q__Propeller=theta[7]
	K_t__Motor=theta[9]
	
	out1 = (2*K_Q__Propeller*x1**2 - 2**(1/2)*3**(1/2)*K_t__Motor*a5)/(2*J_r__MotorProp**2)
	out2 = -x1**2/J_r__MotorProp
	out3 = (2**(1/2)*3**(1/2)*a5)/(2*J_r__MotorProp)
	
	return out1, out2, out3
