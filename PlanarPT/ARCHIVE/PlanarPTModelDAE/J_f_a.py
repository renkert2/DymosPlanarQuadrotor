from numpy import *

def J_f_a(x,a,u,d,theta):
# auto-generated function from matlab

	theta3 = theta[2]
	theta4 = theta[3]
	theta5 = theta[4]
	theta8 = theta[7]
	theta11 = theta[10]
	out1 = -1389/(5000*theta5*theta8) 
	out2 = 463302912568096597869873046875/(39614081257132168796771975168*theta11*(theta3 + theta4)) 
	out3 = 463302912568096597869873046875/(39614081257132168796771975168*theta11*(theta3 + theta4)) 

	return out1, out2, out3
