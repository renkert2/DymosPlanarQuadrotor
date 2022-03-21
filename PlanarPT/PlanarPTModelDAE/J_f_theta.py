from numpy import *

def J_f_theta(x,a,u,d,theta):
# auto-generated function from matlab

	x2=x[1]
	x3=x[2]
	a2=a[1]
	a7=a[6]
	a8=a[7]
	Capacity__Battery=theta[0]
	J_r__MotorProp=theta[6]
	K_Q__Propeller=theta[7]
	K_t__Motor=theta[9]
	
	out1 = a2/Capacity__Battery**2
	out2 = (2*K_Q__Propeller*x2**2 - 2**(1/2)*3**(1/2)*K_t__Motor*a7)/(2*J_r__MotorProp**2)
	out3 = (2*K_Q__Propeller*x3**2 - 2**(1/2)*3**(1/2)*K_t__Motor*a8)/(2*J_r__MotorProp**2)
	out4 = -x2**2/J_r__MotorProp
	out5 = -x3**2/J_r__MotorProp
	out6 = (2**(1/2)*3**(1/2)*a7)/(2*J_r__MotorProp)
	out7 = (2**(1/2)*3**(1/2)*a8)/(2*J_r__MotorProp)
	
	return out1, out2, out3, out4, out5, out6, out7
