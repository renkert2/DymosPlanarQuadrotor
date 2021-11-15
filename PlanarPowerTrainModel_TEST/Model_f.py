import math
import numpy as np

def Calc_f(x,u,d,theta):
# auto-generated function from matlab

	x2 = x[1]
	x3 = x[2]
	u1 = u[0]
	u2 = u[1]
	D__Propeller = theta[1]
	J__Motor = theta[2]
	J__Propeller = theta[3]
	N_p__Battery = theta[4]
	N_s__Battery = theta[5]
	Q__Battery = theta[7]
	R_s__Battery = theta[8]
	Rm__Motor = theta[9]
	kV__Motor = theta[10]
	k_P__Propeller = theta[11]
	k_P_mod__Propeller = theta[12]
	out1 = (250*(300*u1*x2 + 300*u2*x3 - 37*N_s__Battery*kV__Motor*u1**2*np.pi - 37*N_s__Battery*kV__Motor*u2**2*np.pi))/(3*Q__Battery*kV__Motor*np.pi*(300*N_p__Battery + 2000*N_p__Battery*Rm__Motor + 9*N_p__Battery*u1**2 + 9*N_p__Battery*u2**2 + 3000*N_s__Battery*R_s__Battery*u1**2 + 3000*N_s__Battery*R_s__Battery*u2**2)) 
	out2 = -(4*(23439768769181376562500*2**(1/2)*3**(1/2)*6**(1/2)*N_p__Battery*x2 + 703193063075441296875*2**(1/2)*3**(1/2)*6**(1/2)*N_p__Battery*u2**2*x2 + 156265125127875843750000*2**(1/2)*3**(1/2)*6**(1/2)*N_p__Battery*Rm__Motor*x2 + 238484072064614400*D__Propeller**5*N_p__Battery*kV__Motor**2*k_P__Propeller*k_P_mod__Propeller*x2**2*np.pi - 703193063075441296875*2**(1/2)*3**(1/2)*6**(1/2)*N_p__Battery*u1*u2*x3 + 234397687691813765625000*2**(1/2)*3**(1/2)*6**(1/2)*N_s__Battery*R_s__Battery*u2**2*x2 - 2890904814865703109375*2**(1/2)*3**(1/2)*6**(1/2)*N_p__Battery*N_s__Battery*kV__Motor*u1*np.pi + 3179787627528192000*D__Propeller**5*N_p__Battery*Rm__Motor*kV__Motor**2*k_P__Propeller*k_P_mod__Propeller*x2**2*np.pi - 234397687691813765625000*2**(1/2)*3**(1/2)*6**(1/2)*N_s__Battery*R_s__Battery*u1*u2*x3 + 10599292091760640000*D__Propeller**5*N_p__Battery*Rm__Motor**2*kV__Motor**2*k_P__Propeller*k_P_mod__Propeller*x2**2*np.pi + 7154522161938432*D__Propeller**5*N_p__Battery*kV__Motor**2*k_P__Propeller*k_P_mod__Propeller*u1**2*x2**2*np.pi + 7154522161938432*D__Propeller**5*N_p__Battery*kV__Motor**2*k_P__Propeller*k_P_mod__Propeller*u2**2*x2**2*np.pi + 2384840720646144000*D__Propeller**5*N_s__Battery*R_s__Battery*kV__Motor**2*k_P__Propeller*k_P_mod__Propeller*u1**2*x2**2*np.pi + 2384840720646144000*D__Propeller**5*N_s__Battery*R_s__Battery*kV__Motor**2*k_P__Propeller*k_P_mod__Propeller*u2**2*x2**2*np.pi + 47696814412922880*D__Propeller**5*N_p__Battery*Rm__Motor*kV__Motor**2*k_P__Propeller*k_P_mod__Propeller*u1**2*x2**2*np.pi + 47696814412922880*D__Propeller**5*N_p__Battery*Rm__Motor*kV__Motor**2*k_P__Propeller*k_P_mod__Propeller*u2**2*x2**2*np.pi - 19272698765771354062500*2**(1/2)*3**(1/2)*6**(1/2)*N_p__Battery*N_s__Battery*Rm__Motor*kV__Motor*u1*np.pi + 15898938137640960000*D__Propeller**5*N_s__Battery*R_s__Battery*Rm__Motor*kV__Motor**2*k_P__Propeller*k_P_mod__Propeller*u1**2*x2**2*np.pi + 15898938137640960000*D__Propeller**5*N_s__Battery*R_s__Battery*Rm__Motor*kV__Motor**2*k_P__Propeller*k_P_mod__Propeller*u2**2*x2**2*np.pi))/(69451166723500375*kV__Motor**2*np.pi**2*(J__Motor + J__Propeller)*(900*N_p__Battery + 12000*N_p__Battery*Rm__Motor + 40000*N_p__Battery*Rm__Motor**2 + 27*N_p__Battery*u1**2 + 27*N_p__Battery*u2**2 + 9000*N_s__Battery*R_s__Battery*u1**2 + 9000*N_s__Battery*R_s__Battery*u2**2 + 180*N_p__Battery*Rm__Motor*u1**2 + 180*N_p__Battery*Rm__Motor*u2**2 + 60000*N_s__Battery*R_s__Battery*Rm__Motor*u1**2 + 60000*N_s__Battery*R_s__Battery*Rm__Motor*u2**2)) 
	out3 = -(4*(23439768769181376562500*2**(1/2)*3**(1/2)*6**(1/2)*N_p__Battery*x3 + 703193063075441296875*2**(1/2)*3**(1/2)*6**(1/2)*N_p__Battery*u1**2*x3 + 156265125127875843750000*2**(1/2)*3**(1/2)*6**(1/2)*N_p__Battery*Rm__Motor*x3 + 238484072064614400*D__Propeller**5*N_p__Battery*kV__Motor**2*k_P__Propeller*k_P_mod__Propeller*x3**2*np.pi - 703193063075441296875*2**(1/2)*3**(1/2)*6**(1/2)*N_p__Battery*u1*u2*x2 + 234397687691813765625000*2**(1/2)*3**(1/2)*6**(1/2)*N_s__Battery*R_s__Battery*u1**2*x3 - 2890904814865703109375*2**(1/2)*3**(1/2)*6**(1/2)*N_p__Battery*N_s__Battery*kV__Motor*u2*np.pi + 3179787627528192000*D__Propeller**5*N_p__Battery*Rm__Motor*kV__Motor**2*k_P__Propeller*k_P_mod__Propeller*x3**2*np.pi - 234397687691813765625000*2**(1/2)*3**(1/2)*6**(1/2)*N_s__Battery*R_s__Battery*u1*u2*x2 + 10599292091760640000*D__Propeller**5*N_p__Battery*Rm__Motor**2*kV__Motor**2*k_P__Propeller*k_P_mod__Propeller*x3**2*np.pi + 7154522161938432*D__Propeller**5*N_p__Battery*kV__Motor**2*k_P__Propeller*k_P_mod__Propeller*u1**2*x3**2*np.pi + 7154522161938432*D__Propeller**5*N_p__Battery*kV__Motor**2*k_P__Propeller*k_P_mod__Propeller*u2**2*x3**2*np.pi + 2384840720646144000*D__Propeller**5*N_s__Battery*R_s__Battery*kV__Motor**2*k_P__Propeller*k_P_mod__Propeller*u1**2*x3**2*np.pi + 2384840720646144000*D__Propeller**5*N_s__Battery*R_s__Battery*kV__Motor**2*k_P__Propeller*k_P_mod__Propeller*u2**2*x3**2*np.pi + 47696814412922880*D__Propeller**5*N_p__Battery*Rm__Motor*kV__Motor**2*k_P__Propeller*k_P_mod__Propeller*u1**2*x3**2*np.pi + 47696814412922880*D__Propeller**5*N_p__Battery*Rm__Motor*kV__Motor**2*k_P__Propeller*k_P_mod__Propeller*u2**2*x3**2*np.pi - 19272698765771354062500*2**(1/2)*3**(1/2)*6**(1/2)*N_p__Battery*N_s__Battery*Rm__Motor*kV__Motor*u2*np.pi + 15898938137640960000*D__Propeller**5*N_s__Battery*R_s__Battery*Rm__Motor*kV__Motor**2*k_P__Propeller*k_P_mod__Propeller*u1**2*x3**2*np.pi + 15898938137640960000*D__Propeller**5*N_s__Battery*R_s__Battery*Rm__Motor*kV__Motor**2*k_P__Propeller*k_P_mod__Propeller*u2**2*x3**2*np.pi))/(69451166723500375*kV__Motor**2*np.pi**2*(J__Motor + J__Propeller)*(900*N_p__Battery + 12000*N_p__Battery*Rm__Motor + 40000*N_p__Battery*Rm__Motor**2 + 27*N_p__Battery*u1**2 + 27*N_p__Battery*u2**2 + 9000*N_s__Battery*R_s__Battery*u1**2 + 9000*N_s__Battery*R_s__Battery*u2**2 + 180*N_p__Battery*Rm__Motor*u1**2 + 180*N_p__Battery*Rm__Motor*u2**2 + 60000*N_s__Battery*R_s__Battery*Rm__Motor*u1**2 + 60000*N_s__Battery*R_s__Battery*Rm__Motor*u2**2)) 
	return out1, out2, out3
