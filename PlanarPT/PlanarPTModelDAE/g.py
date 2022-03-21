from numpy import *

def g(x,a,u,d,theta):
# auto-generated function from matlab

	x1=x[0]
	x2=x[1]
	x3=x[2]
	a1=a[0]
	a2=a[1]
	a3=a[2]
	a4=a[3]
	a5=a[4]
	a6=a[5]
	a7=a[6]
	a8=a[7]
	u1=u[0]
	u2=u[1]
	Capacity__Battery=theta[0]
	D__Motor=theta[1]
	D__Propeller=theta[2]
	I_max__PMSMInverter_2=theta[3]
	J__Motor=theta[4]
	J__Propeller=theta[5]
	J_r__MotorProp=theta[6]
	K_Q__Propeller=theta[7]
	K_T__Propeller=theta[8]
	K_t__Motor=theta[9]
	Mass__Battery=theta[10]
	Mass__Motor=theta[11]
	Mass__PMSMInverter_2=theta[12]
	Mass__Propeller=theta[13]
	MaxDischarge__Battery=theta[14]
	N_p__Battery=theta[15]
	N_s__Battery=theta[16]
	P__Propeller=theta[17]
	Price__Battery=theta[18]
	Price__Motor=theta[19]
	Price__PMSMInverter_2=theta[20]
	Price__Propeller=theta[21]
	Q__Battery=theta[22]
	R__PMSMInverter_2=theta[23]
	R_p__Battery=theta[24]
	R_s__Battery=theta[25]
	Rm__Motor=theta[26]
	V_OCV_pack__Battery=theta[27]
	kV__Motor=theta[28]
	k_P__Propeller=theta[29]
	k_P_mod__Propeller=theta[30]
	k_Q__Propeller=theta[31]
	k_T__Propeller=theta[32]
	k_T_mod__Propeller=theta[33]
	
	out1 = K_T__Propeller*x2**2
	out2 = K_Q__Propeller*x2**2
	out3 = K_T__Propeller*x3**2
	out4 = K_Q__Propeller*x3**2
	
	return out1, out2, out3, out4
