from numpy import *

def h(x,a,u,d,theta):
# auto-generated function from matlab

	x1 = x[0]
	a1 = a[0]
	a2 = a[1]
	a3 = a[2]
	a4 = a[3]
	a5 = a[4]
	u1 = u[0]
	theta5 = theta[4]
	theta6 = theta[5]
	theta9 = theta[8]
	theta10 = theta[9]
	theta11 = theta[10]
	out1 = a2 - 2*a3*u1 
	out2 = -(a1*theta5 + (3*a2*theta5)/1000 - (37*theta5*theta6)/10 + a2*theta6*theta9)/theta5 
	out3 = a1*u1 - (1633*a4)/2000 - a3/10 
	out4 = (1633*a3)/2000 - a5 
	out5 = -((1028709595972545759*x1)/87960930222080000 - (12499641*a4*theta11)/12500000 + (12499641*a5*theta10*theta11)/12500000)/theta11 

	return out1, out2, out3, out4, out5
