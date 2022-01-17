import math
import numpy as np

def f(x,a,u,d,theta):
# auto-generated function from matlab

	x1 = x[0]
	a5 = a[4]
	theta2 = theta[1]
	theta3 = theta[2]
	theta4 = theta[3]
	theta7 = theta[6]
	theta11 = theta[10]
	theta13 = theta[12]
	out1 = ((463302912568096597869873046875*a5)/39614081257132168796771975168 - (3078954507600442568115234375*theta2**5*theta7*theta11*theta13*x1**2)/633825300114114700748351602688)/(theta11*(theta3 + theta4)) 

	return out1
