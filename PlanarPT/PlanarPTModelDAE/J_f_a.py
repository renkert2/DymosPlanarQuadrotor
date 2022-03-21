from numpy import *

def J_f_a(x,a,u,d,theta):
# auto-generated function from matlab

	Capacity__Battery=theta[0]
	J_r__MotorProp=theta[6]
	K_t__Motor=theta[9]
	
	out1 = -1/Capacity__Battery
	out2 = (2**(1/2)*3**(1/2)*K_t__Motor)/(2*J_r__MotorProp)
	out3 = (2**(1/2)*3**(1/2)*K_t__Motor)/(2*J_r__MotorProp)
	
	return out1, out2, out3
