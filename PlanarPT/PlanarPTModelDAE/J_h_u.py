from numpy import *

def J_h_u(x,a,u,d,theta):
# auto-generated function from matlab

	a1=a[0]
	a3=a[2]
	a5=a[4]
	
	out1 = -a3
	out2 = a1
	out3 = -a5
	out4 = a1
	
	return out1, out2, out3, out4
