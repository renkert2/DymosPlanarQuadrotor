from numpy import *

def h(x,a,u,d,theta):
# auto-generated function from matlab

	x1=x[0]
	a1=a[0]
	a2=a[1]
	a3=a[2]
	a4=a[3]
	a5=a[4]
	u1=u[0]
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
	Mass__PlanarPowerTrain=theta[13]
	Mass__Propeller=theta[14]
	MaxDischarge__Battery=theta[15]
	N_p__Battery=theta[16]
	N_s__Battery=theta[17]
	P__Propeller=theta[18]
	Price__Battery=theta[19]
	Price__Motor=theta[20]
	Price__PMSMInverter_2=theta[21]
	Price__PlanarPowerTrain=theta[22]
	Price__Propeller=theta[23]
	Q__Battery=theta[24]
	R__PMSMInverter_2=theta[25]
	R_p__Battery=theta[26]
	R_s__Battery=theta[27]
	Rm__Motor=theta[28]
	V_OCV_pack__Battery=theta[29]
	kV__Motor=theta[30]
	k_P__Propeller=theta[31]
	k_P_mod__Propeller=theta[32]
	k_Q__Propeller=theta[33]
	k_T__Propeller=theta[34]
	k_T_mod__Propeller=theta[35]
	
	out1 = a2 - 2*a3*u1
	out2 = (37*N_s__Battery)/10 - a1 - (3*a2)/1000 - R_p__Battery*a2
	out3 = a1*u1 - R__PMSMInverter_2*a3 - (2**(1/2)*3**(1/2)*a4)/3
	out4 = (2**(1/2)*3**(1/2)*a3)/3 - a5
	out5 = a4 - Rm__Motor*a5 - (2**(1/2)*3**(1/2)*K_t__Motor*x1)/2
	
	return out1, out2, out3, out4, out5
