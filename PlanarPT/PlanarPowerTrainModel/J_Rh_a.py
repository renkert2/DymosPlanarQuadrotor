import math
import numpy as np

def J_Rh_a(x,a,u,d,theta):
# auto-generated function from matlab

	u1 = u[0]
	u2 = u[1]
	theta5 = theta[4]
	theta6 = theta[5]
	theta9 = theta[8]
	theta10 = theta[9]
	out1 = u1 
	out2 = u2 
	out3 = -((3*theta5)/1000 + theta6*theta9)/theta5 
	out4 = -u1 
	out5 = -u2 
	out6 = -(12499641*theta10)/12500000 
	out7 = -(12499641*theta10)/12500000 

	return out1, out2, out3, out4, out5, out6, out7
