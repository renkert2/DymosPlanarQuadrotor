from numpy import *

def J_h_a(x,a,u,d,theta):
# auto-generated function from matlab

	u1=u[0]
	R__PMSMInverter_2=theta[25]
	R_p__Battery=theta[26]
	Rm__Motor=theta[28]
	
	out1 = u1
	out2 = - R_p__Battery - 3/1000
	out3 = -2*u1
	out4 = -R__PMSMInverter_2
	out5 = -Rm__Motor
	
	return out1, out2, out3, out4, out5
