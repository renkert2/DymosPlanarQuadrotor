import math
import numpy as np

def CalcJ_f_x(x,u,d,theta,nn):
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
	et1 = math.sqrt(2.0)*math.sqrt(3.0)*math.sqrt(6.0)*N_p__Battery*1.35e+6+math.sqrt(2.0)*math.sqrt(3.0)*math.sqrt(6.0)*N_p__Battery*Rm__Motor*9.0e+6+math.sqrt(2.0)*math.sqrt(3.0)*math.sqrt(6.0)*N_p__Battery*u2**2*4.05e+4+K_Q__Propeller*N_p__Battery*kV__Motor**2*x2*np.pi**2*1.8e+3+K_Q__Propeller*N_p__Battery*Rm__Motor*kV__Motor**2*x2*np.pi**2*2.4e+4+K_Q__Propeller*N_p__Battery*Rm__Motor**2*kV__Motor**2*x2*np.pi**2*8.0e+4+K_Q__Propeller*N_p__Battery*kV__Motor**2*u1**2*x2*np.pi**2*5.4e+1+K_Q__Propeller*N_p__Battery*kV__Motor**2*u2**2*x2*np.pi**2*5.4e+1+math.sqrt(2.0)*math.sqrt(3.0)*math.sqrt(6.0)*N_s__Battery*R_s__Battery*u2**2*1.35e+7;
	et2 = K_Q__Propeller*N_s__Battery*R_s__Battery*kV__Motor**2*u1**2*x2*np.pi**2*1.8e+4+K_Q__Propeller*N_s__Battery*R_s__Battery*kV__Motor**2*u2**2*x2*np.pi**2*1.8e+4+K_Q__Propeller*N_p__Battery*Rm__Motor*kV__Motor**2*u1**2*x2*np.pi**2*3.6e+2+K_Q__Propeller*N_p__Battery*Rm__Motor*kV__Motor**2*u2**2*x2*np.pi**2*3.6e+2+K_Q__Propeller*N_s__Battery*R_s__Battery*Rm__Motor*kV__Motor**2*u1**2*x2*np.pi**2*1.2e+5+K_Q__Propeller*N_s__Battery*R_s__Battery*Rm__Motor*kV__Motor**2*u2**2*x2*np.pi**2*1.2e+5;
	et3 = math.sqrt(2.0)*math.sqrt(3.0)*math.sqrt(6.0)*N_p__Battery*1.35e+6+math.sqrt(2.0)*math.sqrt(3.0)*math.sqrt(6.0)*N_p__Battery*Rm__Motor*9.0e+6+math.sqrt(2.0)*math.sqrt(3.0)*math.sqrt(6.0)*N_p__Battery*u1**2*4.05e+4+K_Q__Propeller*N_p__Battery*kV__Motor**2*x3*np.pi**2*1.8e+3+K_Q__Propeller*N_p__Battery*Rm__Motor*kV__Motor**2*x3*np.pi**2*2.4e+4+K_Q__Propeller*N_p__Battery*Rm__Motor**2*kV__Motor**2*x3*np.pi**2*8.0e+4+K_Q__Propeller*N_p__Battery*kV__Motor**2*u1**2*x3*np.pi**2*5.4e+1+K_Q__Propeller*N_p__Battery*kV__Motor**2*u2**2*x3*np.pi**2*5.4e+1+math.sqrt(2.0)*math.sqrt(3.0)*math.sqrt(6.0)*N_s__Battery*R_s__Battery*u1**2*1.35e+7;
	et4 = K_Q__Propeller*N_s__Battery*R_s__Battery*kV__Motor**2*u1**2*x3*np.pi**2*1.8e+4+K_Q__Propeller*N_s__Battery*R_s__Battery*kV__Motor**2*u2**2*x3*np.pi**2*1.8e+4+K_Q__Propeller*N_p__Battery*Rm__Motor*kV__Motor**2*u1**2*x3*np.pi**2*3.6e+2+K_Q__Propeller*N_p__Battery*Rm__Motor*kV__Motor**2*u2**2*x3*np.pi**2*3.6e+2+K_Q__Propeller*N_s__Battery*R_s__Battery*Rm__Motor*kV__Motor**2*u1**2*x3*np.pi**2*1.2e+5+K_Q__Propeller*N_s__Battery*R_s__Battery*Rm__Motor*kV__Motor**2*u2**2*x3*np.pi**2*1.2e+5;
	mt1 = [0.0,0.0,0.0,(u1*2.5e+4)/(Q__Battery*kV__Motor*np.pi*(N_p__Battery*3.0e+2+N_p__Battery*Rm__Motor*2.0e+3+N_p__Battery*u1**2*9.0+N_p__Battery*u2**2*9.0+N_s__Battery*R_s__Battery*u1**2*3.0e+3+N_s__Battery*R_s__Battery*u2**2*3.0e+3)),-(1.0/kV__Motor**2*1.0/np.pi**2*(et1+et2))/(J_r__MotorProp*(N_p__Battery*9.0e+2+N_p__Battery*Rm__Motor*1.2e+4+N_p__Battery*Rm__Motor**2*4.0e+4+N_p__Battery*u1**2*2.7e+1+N_p__Battery*u2**2*2.7e+1+N_s__Battery*R_s__Battery*u1**2*9.0e+3+N_s__Battery*R_s__Battery*u2**2*9.0e+3+N_p__Battery*Rm__Motor*u1**2*1.8e+2+N_p__Battery*Rm__Motor*u2**2*1.8e+2+N_s__Battery*R_s__Battery*Rm__Motor*u1**2*6.0e+4+N_s__Battery*R_s__Battery*Rm__Motor*u2**2*6.0e+4))];
	mt2 = [(1.0/kV__Motor**2*1.0/np.pi**2*(math.sqrt(2.0)*math.sqrt(3.0)*math.sqrt(6.0)*N_p__Battery*u1*u2*4.05e+4+math.sqrt(2.0)*math.sqrt(3.0)*math.sqrt(6.0)*N_s__Battery*R_s__Battery*u1*u2*1.35e+7))/(J_r__MotorProp*(N_p__Battery*9.0e+2+N_p__Battery*Rm__Motor*1.2e+4+N_p__Battery*Rm__Motor**2*4.0e+4+N_p__Battery*u1**2*2.7e+1+N_p__Battery*u2**2*2.7e+1+N_s__Battery*R_s__Battery*u1**2*9.0e+3+N_s__Battery*R_s__Battery*u2**2*9.0e+3+N_p__Battery*Rm__Motor*u1**2*1.8e+2+N_p__Battery*Rm__Motor*u2**2*1.8e+2+N_s__Battery*R_s__Battery*Rm__Motor*u1**2*6.0e+4+N_s__Battery*R_s__Battery*Rm__Motor*u2**2*6.0e+4))];
	mt3 = [(u2*2.5e+4)/(Q__Battery*kV__Motor*np.pi*(N_p__Battery*3.0e+2+N_p__Battery*Rm__Motor*2.0e+3+N_p__Battery*u1**2*9.0+N_p__Battery*u2**2*9.0+N_s__Battery*R_s__Battery*u1**2*3.0e+3+N_s__Battery*R_s__Battery*u2**2*3.0e+3))];
	mt4 = [(1.0/kV__Motor**2*1.0/np.pi**2*(math.sqrt(2.0)*math.sqrt(3.0)*math.sqrt(6.0)*N_p__Battery*u1*u2*4.05e+4+math.sqrt(2.0)*math.sqrt(3.0)*math.sqrt(6.0)*N_s__Battery*R_s__Battery*u1*u2*1.35e+7))/(J_r__MotorProp*(N_p__Battery*9.0e+2+N_p__Battery*Rm__Motor*1.2e+4+N_p__Battery*Rm__Motor**2*4.0e+4+N_p__Battery*u1**2*2.7e+1+N_p__Battery*u2**2*2.7e+1+N_s__Battery*R_s__Battery*u1**2*9.0e+3+N_s__Battery*R_s__Battery*u2**2*9.0e+3+N_p__Battery*Rm__Motor*u1**2*1.8e+2+N_p__Battery*Rm__Motor*u2**2*1.8e+2+N_s__Battery*R_s__Battery*Rm__Motor*u1**2*6.0e+4+N_s__Battery*R_s__Battery*Rm__Motor*u2**2*6.0e+4))];
	mt5 = [-(1.0/kV__Motor**2*1.0/np.pi**2*(et3+et4))/(J_r__MotorProp*(N_p__Battery*9.0e+2+N_p__Battery*Rm__Motor*1.2e+4+N_p__Battery*Rm__Motor**2*4.0e+4+N_p__Battery*u1**2*2.7e+1+N_p__Battery*u2**2*2.7e+1+N_s__Battery*R_s__Battery*u1**2*9.0e+3+N_s__Battery*R_s__Battery*u2**2*9.0e+3+N_p__Battery*Rm__Motor*u1**2*1.8e+2+N_p__Battery*Rm__Motor*u2**2*1.8e+2+N_s__Battery*R_s__Battery*Rm__Motor*u1**2*6.0e+4+N_s__Battery*R_s__Battery*Rm__Motor*u2**2*6.0e+4))];
	out = np.concatenate([mt1,mt2,mt3,mt4,mt5]);
	out_temp = [];
	for i in range(nn):
		l = [out[j,i] for j in range(9)]
		l=np.reshape(l, (3,3))
		out_temp.append(l)
	out = out_temp

	return out