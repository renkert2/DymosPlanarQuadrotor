from numpy import *

def J_f_x(x,a,u,d,theta):
# auto-generated function from matlab

	x1 = x[0]
	theta2 = theta[1]
	theta3 = theta[2]
	theta4 = theta[3]
	theta7 = theta[6]
	theta13 = theta[12]
	out1 = -(3078954507600442568115234375*theta2**5*theta7*theta13*x1)/(316912650057057350374175801344*(theta3 + theta4)) 

	return out1
