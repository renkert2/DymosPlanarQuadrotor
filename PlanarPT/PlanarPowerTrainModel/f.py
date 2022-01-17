from numpy import *

def f(x,a,u,d,theta):
# auto-generated function from matlab

	x2 = x[1]
	x3 = x[2]
	a2 = a[1]
	a7 = a[6]
	a8 = a[7]
	theta2 = theta[1]
	theta3 = theta[2]
	theta4 = theta[3]
	theta5 = theta[4]
	theta7 = theta[6]
	theta8 = theta[7]
	theta11 = theta[10]
	theta13 = theta[12]
	out1 = -(1389*a2)/(5000*theta5*theta8) 
	out2 = ((463302912568096597869873046875*a7)/39614081257132168796771975168 - (3078954507600442568115234375*theta2**5*theta7*theta11*theta13*x2**2)/633825300114114700748351602688)/(theta11*(theta3 + theta4)) 
	out3 = ((463302912568096597869873046875*a8)/39614081257132168796771975168 - (3078954507600442568115234375*theta2**5*theta7*theta11*theta13*x3**2)/633825300114114700748351602688)/(theta11*(theta3 + theta4)) 

	return out1, out2, out3
