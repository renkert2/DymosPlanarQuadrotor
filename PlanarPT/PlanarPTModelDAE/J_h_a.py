from numpy import *

def J_h_a(x,a,u,d,theta):
# auto-generated function from matlab

	u1=u[0]
	u2=u[1]
	R__PMSMInverter_2=theta[25]
	R_p__Battery=theta[26]
	Rm__Motor=theta[28]
	
	out1 = u1
	out2 = u2
	out3 = - R_p__Battery - 3/1000
	out4 = -u1
	out5 = -R__PMSMInverter_2
	out6 = -u2
	out7 = -R__PMSMInverter_2
	out8 = -Rm__Motor
	out9 = -Rm__Motor
	
	return out1, out2, out3, out4, out5, out6, out7, out8, out9
