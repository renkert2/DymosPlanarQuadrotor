from numpy import *

def J_h_theta(x,a,u,d,theta):
# auto-generated function from matlab

	x2=x[1]
	x3=x[2]
	a2=a[1]
	a3=a[2]
	a5=a[4]
	a7=a[6]
	a8=a[7]
	
	out1 = -(2**(1/2)*3**(1/2)*x2)/2
	out2 = -(2**(1/2)*3**(1/2)*x3)/2
	out3 = -a3
	out4 = -a5
	out5 = -a2
	out6 = -a7
	out7 = -a8
	
	return out1, out2, out3, out4, out5, out6, out7
