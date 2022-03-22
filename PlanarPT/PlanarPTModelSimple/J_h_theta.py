from numpy import *

def J_h_theta(x,a,u,d,theta):
# auto-generated function from matlab

	x1=x[0]
	a2=a[1]
	a3=a[2]
	a5=a[4]
	
	out1 = -(2**(1/2)*3**(1/2)*x1)/2
	out2 = -a3
	out3 = -a2
	out4 = -a5
	
	return out1, out2, out3, out4
