import math
import numpy as np

def Calc_f(x,u,d,theta,nn):
# auto-generated function from matlab
	J_r__MotorProp = theta[4];
	K_Q__Propeller = theta[5];
	N_p__Battery = theta[7];
	N_s__Battery = theta[8];
	Q__Battery = theta[10];
	R_s__Battery = theta[11];
	Rm__Motor = theta[12];
	kV__Motor = theta[13];
	u1 = u[0];
	u2 = u[1];
	x2 = x[1];
	x3 = x[2];
	et1 = math.sqrt(2.0)*math.sqrt(3.0)*math.sqrt(6.0)*N_p__Battery*x3*1.35e+6+K_Q__Propeller*N_p__Battery*kV__Motor**2*x3**2*np.pi**2*9.0e+2+math.sqrt(2.0)*math.sqrt(3.0)*math.sqrt(6.0)*N_p__Battery*u1**2*x3*4.05e+4+K_Q__Propeller*N_p__Battery*kV__Motor**2*u1**2*x3**2*np.pi**2*2.7e+1+K_Q__Propeller*N_p__Battery*kV__Motor**2*u2**2*x3**2*np.pi**2*2.7e+1+math.sqrt(2.0)*math.sqrt(3.0)*math.sqrt(6.0)*N_p__Battery*Rm__Motor*x3*9.0e+6+K_Q__Propeller*N_p__Battery*Rm__Motor*kV__Motor**2*x3**2*np.pi**2*1.2e+4+K_Q__Propeller*N_p__Battery*Rm__Motor**2*kV__Motor**2*x3**2*np.pi**2*4.0e+4-math.sqrt(2.0)*math.sqrt(3.0)*math.sqrt(6.0)*N_p__Battery*u1*u2*x2*4.05e+4;
	et2 = math.sqrt(2.0)*math.sqrt(3.0)*math.sqrt(6.0)*N_s__Battery*R_s__Battery*u1**2*x3*1.35e+7+K_Q__Propeller*N_s__Battery*R_s__Battery*kV__Motor**2*u1**2*x3**2*np.pi**2*9.0e+3+K_Q__Propeller*N_s__Battery*R_s__Battery*kV__Motor**2*u2**2*x3**2*np.pi**2*9.0e+3+K_Q__Propeller*N_p__Battery*Rm__Motor*kV__Motor**2*u1**2*x3**2*np.pi**2*1.8e+2+K_Q__Propeller*N_p__Battery*Rm__Motor*kV__Motor**2*u2**2*x3**2*np.pi**2*1.8e+2-math.sqrt(2.0)*math.sqrt(3.0)*math.sqrt(6.0)*N_p__Battery*N_s__Battery*kV__Motor*u2*np.pi*1.665e+5-math.sqrt(2.0)*math.sqrt(3.0)*math.sqrt(6.0)*N_s__Battery*R_s__Battery*u1*u2*x2*1.35e+7+K_Q__Propeller*N_s__Battery*R_s__Battery*Rm__Motor*kV__Motor**2*u1**2*x3**2*np.pi**2*6.0e+4;
	et3 = K_Q__Propeller*N_s__Battery*R_s__Battery*Rm__Motor*kV__Motor**2*u2**2*x3**2*np.pi**2*6.0e+4-math.sqrt(2.0)*math.sqrt(3.0)*math.sqrt(6.0)*N_p__Battery*N_s__Battery*Rm__Motor*kV__Motor*u2*np.pi*1.11e+6;
	et4 = math.sqrt(2.0)*math.sqrt(3.0)*math.sqrt(6.0)*N_p__Battery*x2*1.35e+6+K_Q__Propeller*N_p__Battery*kV__Motor**2*x2**2*np.pi**2*9.0e+2+math.sqrt(2.0)*math.sqrt(3.0)*math.sqrt(6.0)*N_p__Battery*u2**2*x2*4.05e+4+K_Q__Propeller*N_p__Battery*kV__Motor**2*u1**2*x2**2*np.pi**2*2.7e+1+K_Q__Propeller*N_p__Battery*kV__Motor**2*u2**2*x2**2*np.pi**2*2.7e+1+math.sqrt(2.0)*math.sqrt(3.0)*math.sqrt(6.0)*N_p__Battery*Rm__Motor*x2*9.0e+6+K_Q__Propeller*N_p__Battery*Rm__Motor*kV__Motor**2*x2**2*np.pi**2*1.2e+4+K_Q__Propeller*N_p__Battery*Rm__Motor**2*kV__Motor**2*x2**2*np.pi**2*4.0e+4-math.sqrt(2.0)*math.sqrt(3.0)*math.sqrt(6.0)*N_p__Battery*u1*u2*x3*4.05e+4;
	et5 = math.sqrt(2.0)*math.sqrt(3.0)*math.sqrt(6.0)*N_s__Battery*R_s__Battery*u2**2*x2*1.35e+7+K_Q__Propeller*N_s__Battery*R_s__Battery*kV__Motor**2*u1**2*x2**2*np.pi**2*9.0e+3+K_Q__Propeller*N_s__Battery*R_s__Battery*kV__Motor**2*u2**2*x2**2*np.pi**2*9.0e+3+K_Q__Propeller*N_p__Battery*Rm__Motor*kV__Motor**2*u1**2*x2**2*np.pi**2*1.8e+2+K_Q__Propeller*N_p__Battery*Rm__Motor*kV__Motor**2*u2**2*x2**2*np.pi**2*1.8e+2-math.sqrt(2.0)*math.sqrt(3.0)*math.sqrt(6.0)*N_p__Battery*N_s__Battery*kV__Motor*u1*np.pi*1.665e+5-math.sqrt(2.0)*math.sqrt(3.0)*math.sqrt(6.0)*N_s__Battery*R_s__Battery*u1*u2*x3*1.35e+7+K_Q__Propeller*N_s__Battery*R_s__Battery*Rm__Motor*kV__Motor**2*u1**2*x2**2*np.pi**2*6.0e+4;
	et6 = K_Q__Propeller*N_s__Battery*R_s__Battery*Rm__Motor*kV__Motor**2*u2**2*x2**2*np.pi**2*6.0e+4-math.sqrt(2.0)*math.sqrt(3.0)*math.sqrt(6.0)*N_p__Battery*N_s__Battery*Rm__Motor*kV__Motor*u1*np.pi*1.11e+6;
	mt1 = [((u1*x2*3.0e+2+u2*x3*3.0e+2-N_s__Battery*kV__Motor*u1**2*np.pi*3.7e+1-N_s__Battery*kV__Motor*u2**2*np.pi*3.7e+1)*(2.5e+2/3.0))/(Q__Battery*kV__Motor*np.pi*(N_p__Battery*3.0e+2+N_p__Battery*Rm__Motor*2.0e+3+N_p__Battery*u1**2*9.0+N_p__Battery*u2**2*9.0+N_s__Battery*R_s__Battery*u1**2*3.0e+3+N_s__Battery*R_s__Battery*u2**2*3.0e+3))];
	mt2 = [-(1.0/kV__Motor**2*1.0/np.pi**2*(et4+et5+et6))/(J_r__MotorProp*(N_p__Battery*9.0e+2+N_p__Battery*Rm__Motor*1.2e+4+N_p__Battery*Rm__Motor**2*4.0e+4+N_p__Battery*u1**2*2.7e+1+N_p__Battery*u2**2*2.7e+1+N_s__Battery*R_s__Battery*u1**2*9.0e+3+N_s__Battery*R_s__Battery*u2**2*9.0e+3+N_p__Battery*Rm__Motor*u1**2*1.8e+2+N_p__Battery*Rm__Motor*u2**2*1.8e+2+N_s__Battery*R_s__Battery*Rm__Motor*u1**2*6.0e+4+N_s__Battery*R_s__Battery*Rm__Motor*u2**2*6.0e+4))];
	mt3 = [-(1.0/kV__Motor**2*1.0/np.pi**2*(et1+et2+et3))/(J_r__MotorProp*(N_p__Battery*9.0e+2+N_p__Battery*Rm__Motor*1.2e+4+N_p__Battery*Rm__Motor**2*4.0e+4+N_p__Battery*u1**2*2.7e+1+N_p__Battery*u2**2*2.7e+1+N_s__Battery*R_s__Battery*u1**2*9.0e+3+N_s__Battery*R_s__Battery*u2**2*9.0e+3+N_p__Battery*Rm__Motor*u1**2*1.8e+2+N_p__Battery*Rm__Motor*u2**2*1.8e+2+N_s__Battery*R_s__Battery*Rm__Motor*u1**2*6.0e+4+N_s__Battery*R_s__Battery*Rm__Motor*u2**2*6.0e+4))];
	out = np.concatenate([mt1,mt2,mt3]);
	out_temp = [];
	for i in range(nn):
		l = [out[j,i] for j in range(3)]
		l=np.reshape(l, (3,1))
		out_temp.append(l)
	out = out_temp

	return out