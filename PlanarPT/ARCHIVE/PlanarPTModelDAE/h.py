from numpy import *

def h(x,a,u,d,theta):
# auto-generated function from matlab

	x2 = x[1]
	x3 = x[2]
	a1 = a[0]
	a2 = a[1]
	a3 = a[2]
	a4 = a[3]
	a5 = a[4]
	a6 = a[5]
	a7 = a[6]
	a8 = a[7]
	u1 = u[0]
	u2 = u[1]
	theta5 = theta[4]
	theta6 = theta[5]
	theta9 = theta[8]
	theta10 = theta[9]
	theta11 = theta[10]
	out1 = a2 - a3*u1 - a5*u2 
	out2 = -(a1*theta5 + (3*a2*theta5)/1000 - (37*theta5*theta6)/10 + a2*theta6*theta9)/theta5 
	out3 = a1*u1 - (1633*a4)/2000 - a3/10 
	out4 = (1633*a3)/2000 - a7 
	out5 = a1*u2 - (1633*a6)/2000 - a5/10 
	out6 = (1633*a5)/2000 - a8 
	out7 = -((1028709595972545759*x2)/87960930222080000 - (12499641*a4*theta11)/12500000 + (12499641*a7*theta10*theta11)/12500000)/theta11 
	out8 = -((1028709595972545759*x3)/87960930222080000 - (12499641*a6*theta11)/12500000 + (12499641*a8*theta10*theta11)/12500000)/theta11 

	return out1, out2, out3, out4, out5, out6, out7, out8
