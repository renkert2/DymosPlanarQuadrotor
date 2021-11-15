import math
import numpy as np

def Calc_g(x,u,d,theta):
# auto-generated function from matlab

	x1 = x[0]
	x2 = x[1]
	x3 = x[2]
	u1 = u[0]
	u2 = u[1]
	D__Propeller = theta[1]
	N_p__Battery = theta[4]
	N_s__Battery = theta[5]
	R_s__Battery = theta[8]
	Rm__Motor = theta[9]
	kV__Motor = theta[10]
	k_P__Propeller = theta[11]
	k_P_mod__Propeller = theta[12]
	k_T__Propeller = theta[13]
	k_T_mod__Propeller = theta[14]
	out1 = x1 
	out2 = x2 
	out3 = x3 
	out4 = (10*(27*N_p__Battery*u1*x2 + 27*N_p__Battery*u2*x3 + 111*N_p__Battery*N_s__Battery*kV__Motor*np.pi + 9000*N_s__Battery*R_s__Battery*u1*x2 + 9000*N_s__Battery*R_s__Battery*u2*x3 + 740*N_p__Battery*N_s__Battery*Rm__Motor*kV__Motor*np.pi))/(kV__Motor*np.pi*(300*N_p__Battery + 2000*N_p__Battery*Rm__Motor + 9*N_p__Battery*u1**2 + 9*N_p__Battery*u2**2 + 3000*N_s__Battery*R_s__Battery*u1**2 + 3000*N_s__Battery*R_s__Battery*u2**2)) 
	out5 = -(300*(300*N_p__Battery*u1*x2 + 300*N_p__Battery*u2*x3 - 37*N_p__Battery*N_s__Battery*kV__Motor*u1**2*np.pi - 37*N_p__Battery*N_s__Battery*kV__Motor*u2**2*np.pi))/(kV__Motor*np.pi*(300*N_p__Battery + 2000*N_p__Battery*Rm__Motor + 9*N_p__Battery*u1**2 + 9*N_p__Battery*u2**2 + 3000*N_s__Battery*R_s__Battery*u1**2 + 3000*N_s__Battery*R_s__Battery*u2**2)) 
	out6 = -(300*(900*N_p__Battery*x2 + 6000*N_p__Battery*Rm__Motor*x2 + 27*N_p__Battery*u2**2*x2 - 27*N_p__Battery*u1*u2*x3 + 9000*N_s__Battery*R_s__Battery*u2**2*x2 - 111*N_p__Battery*N_s__Battery*kV__Motor*u1*np.pi - 9000*N_s__Battery*R_s__Battery*u1*u2*x3 - 740*N_p__Battery*N_s__Battery*Rm__Motor*kV__Motor*u1*np.pi))/(kV__Motor*np.pi*(900*N_p__Battery + 12000*N_p__Battery*Rm__Motor + 40000*N_p__Battery*Rm__Motor**2 + 27*N_p__Battery*u1**2 + 27*N_p__Battery*u2**2 + 9000*N_s__Battery*R_s__Battery*u1**2 + 9000*N_s__Battery*R_s__Battery*u2**2 + 180*N_p__Battery*Rm__Motor*u1**2 + 180*N_p__Battery*Rm__Motor*u2**2 + 60000*N_s__Battery*R_s__Battery*Rm__Motor*u1**2 + 60000*N_s__Battery*R_s__Battery*Rm__Motor*u2**2)) 
	out7 = (5*6**(1/2)*(2700*N_p__Battery*x2 + 18000*N_p__Battery*Rm__Motor*x2 + 81*N_p__Battery*u1**2*x2 + 81*N_p__Battery*u2**2*x2 + 27000*N_s__Battery*R_s__Battery*u1**2*x2 + 27000*N_s__Battery*R_s__Battery*u2**2*x2 + 540*N_p__Battery*Rm__Motor*u1**2*x2 + 540*N_p__Battery*Rm__Motor*u1*u2*x3 + 180000*N_s__Battery*R_s__Battery*Rm__Motor*u1**2*x2 + 2220*N_p__Battery*N_s__Battery*Rm__Motor*kV__Motor*u1*np.pi + 180000*N_s__Battery*R_s__Battery*Rm__Motor*u1*u2*x3 + 14800*N_p__Battery*N_s__Battery*Rm__Motor**2*kV__Motor*u1*np.pi))/(kV__Motor*np.pi*(900*N_p__Battery + 12000*N_p__Battery*Rm__Motor + 40000*N_p__Battery*Rm__Motor**2 + 27*N_p__Battery*u1**2 + 27*N_p__Battery*u2**2 + 9000*N_s__Battery*R_s__Battery*u1**2 + 9000*N_s__Battery*R_s__Battery*u2**2 + 180*N_p__Battery*Rm__Motor*u1**2 + 180*N_p__Battery*Rm__Motor*u2**2 + 60000*N_s__Battery*R_s__Battery*Rm__Motor*u1**2 + 60000*N_s__Battery*R_s__Battery*Rm__Motor*u2**2)) 
	out8 = -(300*(900*N_p__Battery*x3 + 6000*N_p__Battery*Rm__Motor*x3 + 27*N_p__Battery*u1**2*x3 - 27*N_p__Battery*u1*u2*x2 + 9000*N_s__Battery*R_s__Battery*u1**2*x3 - 111*N_p__Battery*N_s__Battery*kV__Motor*u2*np.pi - 9000*N_s__Battery*R_s__Battery*u1*u2*x2 - 740*N_p__Battery*N_s__Battery*Rm__Motor*kV__Motor*u2*np.pi))/(kV__Motor*np.pi*(900*N_p__Battery + 12000*N_p__Battery*Rm__Motor + 40000*N_p__Battery*Rm__Motor**2 + 27*N_p__Battery*u1**2 + 27*N_p__Battery*u2**2 + 9000*N_s__Battery*R_s__Battery*u1**2 + 9000*N_s__Battery*R_s__Battery*u2**2 + 180*N_p__Battery*Rm__Motor*u1**2 + 180*N_p__Battery*Rm__Motor*u2**2 + 60000*N_s__Battery*R_s__Battery*Rm__Motor*u1**2 + 60000*N_s__Battery*R_s__Battery*Rm__Motor*u2**2)) 
	out9 = (5*6**(1/2)*(2700*N_p__Battery*x3 + 18000*N_p__Battery*Rm__Motor*x3 + 81*N_p__Battery*u1**2*x3 + 81*N_p__Battery*u2**2*x3 + 27000*N_s__Battery*R_s__Battery*u1**2*x3 + 27000*N_s__Battery*R_s__Battery*u2**2*x3 + 540*N_p__Battery*Rm__Motor*u2**2*x3 + 540*N_p__Battery*Rm__Motor*u1*u2*x2 + 180000*N_s__Battery*R_s__Battery*Rm__Motor*u2**2*x3 + 2220*N_p__Battery*N_s__Battery*Rm__Motor*kV__Motor*u2*np.pi + 180000*N_s__Battery*R_s__Battery*Rm__Motor*u1*u2*x2 + 14800*N_p__Battery*N_s__Battery*Rm__Motor**2*kV__Motor*u2*np.pi))/(kV__Motor*np.pi*(900*N_p__Battery + 12000*N_p__Battery*Rm__Motor + 40000*N_p__Battery*Rm__Motor**2 + 27*N_p__Battery*u1**2 + 27*N_p__Battery*u2**2 + 9000*N_s__Battery*R_s__Battery*u1**2 + 9000*N_s__Battery*R_s__Battery*u2**2 + 180*N_p__Battery*Rm__Motor*u1**2 + 180*N_p__Battery*Rm__Motor*u2**2 + 60000*N_s__Battery*R_s__Battery*Rm__Motor*u1**2 + 60000*N_s__Battery*R_s__Battery*Rm__Motor*u2**2)) 
	out10 = -(100*6**(1/2)*(900*N_p__Battery*x2 + 6000*N_p__Battery*Rm__Motor*x2 + 27*N_p__Battery*u2**2*x2 - 27*N_p__Battery*u1*u2*x3 + 9000*N_s__Battery*R_s__Battery*u2**2*x2 - 111*N_p__Battery*N_s__Battery*kV__Motor*u1*np.pi - 9000*N_s__Battery*R_s__Battery*u1*u2*x3 - 740*N_p__Battery*N_s__Battery*Rm__Motor*kV__Motor*u1*np.pi))/(kV__Motor*np.pi*(900*N_p__Battery + 12000*N_p__Battery*Rm__Motor + 40000*N_p__Battery*Rm__Motor**2 + 27*N_p__Battery*u1**2 + 27*N_p__Battery*u2**2 + 9000*N_s__Battery*R_s__Battery*u1**2 + 9000*N_s__Battery*R_s__Battery*u2**2 + 180*N_p__Battery*Rm__Motor*u1**2 + 180*N_p__Battery*Rm__Motor*u2**2 + 60000*N_s__Battery*R_s__Battery*Rm__Motor*u1**2 + 60000*N_s__Battery*R_s__Battery*Rm__Motor*u2**2)) 
	out11 = -(100*6**(1/2)*(900*N_p__Battery*x3 + 6000*N_p__Battery*Rm__Motor*x3 + 27*N_p__Battery*u1**2*x3 - 27*N_p__Battery*u1*u2*x2 + 9000*N_s__Battery*R_s__Battery*u1**2*x3 - 111*N_p__Battery*N_s__Battery*kV__Motor*u2*np.pi - 9000*N_s__Battery*R_s__Battery*u1*u2*x2 - 740*N_p__Battery*N_s__Battery*Rm__Motor*kV__Motor*u2*np.pi))/(kV__Motor*np.pi*(900*N_p__Battery + 12000*N_p__Battery*Rm__Motor + 40000*N_p__Battery*Rm__Motor**2 + 27*N_p__Battery*u1**2 + 27*N_p__Battery*u2**2 + 9000*N_s__Battery*R_s__Battery*u1**2 + 9000*N_s__Battery*R_s__Battery*u2**2 + 180*N_p__Battery*Rm__Motor*u1**2 + 180*N_p__Battery*Rm__Motor*u2**2 + 60000*N_s__Battery*R_s__Battery*Rm__Motor*u1**2 + 60000*N_s__Battery*R_s__Battery*Rm__Motor*u2**2)) 
	out12 = (2119858418352128*D__Propeller**4*k_T__Propeller*k_T_mod__Propeller*x2**2)/69451166723500375 
	out13 = (1059929209176064*D__Propeller**5*k_P__Propeller*k_P_mod__Propeller*x2**2)/(69451166723500375*np.pi) 
	out14 = (2119858418352128*D__Propeller**4*k_T__Propeller*k_T_mod__Propeller*x3**2)/69451166723500375 
	out15 = (1059929209176064*D__Propeller**5*k_P__Propeller*k_P_mod__Propeller*x3**2)/(69451166723500375*np.pi) 
	return out1, out2, out3, out4, out5, out6, out7, out8, out9, out10, out11, out12, out13, out14, out15
