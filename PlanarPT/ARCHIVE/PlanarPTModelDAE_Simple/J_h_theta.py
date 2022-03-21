from numpy import *

def J_h_theta(x,a,u,d,theta):
# auto-generated function from matlab

	x1 = x[0]
	a1 = a[0]
	a2 = a[1]
	a4 = a[3]
	a5 = a[4]
	theta5 = theta[4]
	theta6 = theta[5]
	theta9 = theta[8]
	theta10 = theta[9]
	theta11 = theta[10]
	out1 = (a1*theta5 + (3*a2*theta5)/1000 - (37*theta5*theta6)/10 + a2*theta6*theta9)/theta5**2 - (a1 + (3*a2)/1000 - (37*theta6)/10)/theta5 
	out2 = ((37*theta5)/10 - a2*theta9)/theta5 
	out3 = -(a2*theta6)/theta5 
	out4 = -(12499641*a5)/12500000 
	out5 = ((12499641*a4)/12500000 - (12499641*a5*theta10)/12500000)/theta11 + ((1028709595972545759*x1)/87960930222080000 - (12499641*a4*theta11)/12500000 + (12499641*a5*theta10*theta11)/12500000)/theta11**2 

	return out1, out2, out3, out4, out5
