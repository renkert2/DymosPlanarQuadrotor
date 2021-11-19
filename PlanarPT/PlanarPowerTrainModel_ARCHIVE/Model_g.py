import math
import numpy as np

def Calc_g(x,u,d,theta,nn):
# auto-generated function from matlab
	K_Q__Propeller = theta[5];
	K_T__Propeller = theta[6];
	N_p__Battery = theta[7];
	N_s__Battery = theta[8];
	R_s__Battery = theta[11];
	Rm__Motor = theta[12];
	kV__Motor = theta[13];
	u1 = u[0];
	u2 = u[1];
	x1 = x[0];
	x2 = x[1];
	x3 = x[2];
	et1 = (math.sqrt(6.0)*(N_p__Battery*x3*9.0e+2+N_p__Battery*Rm__Motor*x3*6.0e+3+N_p__Battery*u1**2*x3*2.7e+1-N_p__Battery*u1*u2*x2*2.7e+1+N_s__Battery*R_s__Battery*u1**2*x3*9.0e+3-N_p__Battery*N_s__Battery*kV__Motor*u2*np.pi*1.11e+2-N_s__Battery*R_s__Battery*u1*u2*x2*9.0e+3-N_p__Battery*N_s__Battery*Rm__Motor*kV__Motor*u2*np.pi*7.4e+2))/(kV__Motor*np.pi*(N_p__Battery*9.0e+2+N_p__Battery*Rm__Motor*1.2e+4+N_p__Battery*Rm__Motor**2*4.0e+4+N_p__Battery*u1**2*2.7e+1+N_p__Battery*u2**2*2.7e+1+N_s__Battery*R_s__Battery*u1**2*9.0e+3+N_s__Battery*R_s__Battery*u2**2*9.0e+3+N_p__Battery*Rm__Motor*u1**2*1.8e+2+N_p__Battery*Rm__Motor*u2**2*1.8e+2+N_s__Battery*R_s__Battery*Rm__Motor*u1**2*6.0e+4+N_s__Battery*R_s__Battery*Rm__Motor*u2**2*6.0e+4));
	et2 = -1.0e+2;
	et3 = (math.sqrt(6.0)*(N_p__Battery*x2*9.0e+2+N_p__Battery*Rm__Motor*x2*6.0e+3+N_p__Battery*u2**2*x2*2.7e+1-N_p__Battery*u1*u2*x3*2.7e+1+N_s__Battery*R_s__Battery*u2**2*x2*9.0e+3-N_p__Battery*N_s__Battery*kV__Motor*u1*np.pi*1.11e+2-N_s__Battery*R_s__Battery*u1*u2*x3*9.0e+3-N_p__Battery*N_s__Battery*Rm__Motor*kV__Motor*u1*np.pi*7.4e+2))/(kV__Motor*np.pi*(N_p__Battery*9.0e+2+N_p__Battery*Rm__Motor*1.2e+4+N_p__Battery*Rm__Motor**2*4.0e+4+N_p__Battery*u1**2*2.7e+1+N_p__Battery*u2**2*2.7e+1+N_s__Battery*R_s__Battery*u1**2*9.0e+3+N_s__Battery*R_s__Battery*u2**2*9.0e+3+N_p__Battery*Rm__Motor*u1**2*1.8e+2+N_p__Battery*Rm__Motor*u2**2*1.8e+2+N_s__Battery*R_s__Battery*Rm__Motor*u1**2*6.0e+4+N_s__Battery*R_s__Battery*Rm__Motor*u2**2*6.0e+4));
	et4 = -1.0e+2;
	et5 = math.sqrt(6.0)/(kV__Motor*np.pi*(N_p__Battery*9.0e+2+N_p__Battery*Rm__Motor*1.2e+4+N_p__Battery*Rm__Motor**2*4.0e+4+N_p__Battery*u1**2*2.7e+1+N_p__Battery*u2**2*2.7e+1+N_s__Battery*R_s__Battery*u1**2*9.0e+3+N_s__Battery*R_s__Battery*u2**2*9.0e+3+N_p__Battery*Rm__Motor*u1**2*1.8e+2+N_p__Battery*Rm__Motor*u2**2*1.8e+2+N_s__Battery*R_s__Battery*Rm__Motor*u1**2*6.0e+4+N_s__Battery*R_s__Battery*Rm__Motor*u2**2*6.0e+4));
	et6 = (N_p__Battery*x3*2.7e+3+N_p__Battery*Rm__Motor*x3*1.8e+4+N_p__Battery*u1**2*x3*8.1e+1+N_p__Battery*u2**2*x3*8.1e+1+N_s__Battery*R_s__Battery*u1**2*x3*2.7e+4+N_s__Battery*R_s__Battery*u2**2*x3*2.7e+4+N_p__Battery*Rm__Motor*u2**2*x3*5.4e+2+N_p__Battery*Rm__Motor*u1*u2*x2*5.4e+2+N_s__Battery*R_s__Battery*Rm__Motor*u2**2*x3*1.8e+5+N_p__Battery*N_s__Battery*Rm__Motor*kV__Motor*u2*np.pi*2.22e+3+N_s__Battery*R_s__Battery*Rm__Motor*u1*u2*x2*1.8e+5+N_p__Battery*N_s__Battery*Rm__Motor**2*kV__Motor*u2*np.pi*1.48e+4)*5.0;
	et7 = math.sqrt(6.0)/(kV__Motor*np.pi*(N_p__Battery*9.0e+2+N_p__Battery*Rm__Motor*1.2e+4+N_p__Battery*Rm__Motor**2*4.0e+4+N_p__Battery*u1**2*2.7e+1+N_p__Battery*u2**2*2.7e+1+N_s__Battery*R_s__Battery*u1**2*9.0e+3+N_s__Battery*R_s__Battery*u2**2*9.0e+3+N_p__Battery*Rm__Motor*u1**2*1.8e+2+N_p__Battery*Rm__Motor*u2**2*1.8e+2+N_s__Battery*R_s__Battery*Rm__Motor*u1**2*6.0e+4+N_s__Battery*R_s__Battery*Rm__Motor*u2**2*6.0e+4));
	et8 = (N_p__Battery*x2*2.7e+3+N_p__Battery*Rm__Motor*x2*1.8e+4+N_p__Battery*u1**2*x2*8.1e+1+N_p__Battery*u2**2*x2*8.1e+1+N_s__Battery*R_s__Battery*u1**2*x2*2.7e+4+N_s__Battery*R_s__Battery*u2**2*x2*2.7e+4+N_p__Battery*Rm__Motor*u1**2*x2*5.4e+2+N_p__Battery*Rm__Motor*u1*u2*x3*5.4e+2+N_s__Battery*R_s__Battery*Rm__Motor*u1**2*x2*1.8e+5+N_p__Battery*N_s__Battery*Rm__Motor*kV__Motor*u1*np.pi*2.22e+3+N_s__Battery*R_s__Battery*Rm__Motor*u1*u2*x3*1.8e+5+N_p__Battery*N_s__Battery*Rm__Motor**2*kV__Motor*u1*np.pi*1.48e+4)*5.0;
	mt1 = [x1,x2,x3,((N_p__Battery*u1*x2*2.7e+1+N_p__Battery*u2*x3*2.7e+1+N_p__Battery*N_s__Battery*kV__Motor*np.pi*1.11e+2+N_s__Battery*R_s__Battery*u1*x2*9.0e+3+N_s__Battery*R_s__Battery*u2*x3*9.0e+3+N_p__Battery*N_s__Battery*Rm__Motor*kV__Motor*np.pi*7.4e+2)*1.0e+1)/(kV__Motor*np.pi*(N_p__Battery*3.0e+2+N_p__Battery*Rm__Motor*2.0e+3+N_p__Battery*u1**2*9.0+N_p__Battery*u2**2*9.0+N_s__Battery*R_s__Battery*u1**2*3.0e+3+N_s__Battery*R_s__Battery*u2**2*3.0e+3))];
	mt2 = [((N_p__Battery*u1*x2*3.0e+2+N_p__Battery*u2*x3*3.0e+2-N_p__Battery*N_s__Battery*kV__Motor*u1**2*np.pi*3.7e+1-N_p__Battery*N_s__Battery*kV__Motor*u2**2*np.pi*3.7e+1)*-3.0e+2)/(kV__Motor*np.pi*(N_p__Battery*3.0e+2+N_p__Battery*Rm__Motor*2.0e+3+N_p__Battery*u1**2*9.0+N_p__Battery*u2**2*9.0+N_s__Battery*R_s__Battery*u1**2*3.0e+3+N_s__Battery*R_s__Battery*u2**2*3.0e+3))];
	mt3 = [((N_p__Battery*x2*9.0e+2+N_p__Battery*Rm__Motor*x2*6.0e+3+N_p__Battery*u2**2*x2*2.7e+1-N_p__Battery*u1*u2*x3*2.7e+1+N_s__Battery*R_s__Battery*u2**2*x2*9.0e+3-N_p__Battery*N_s__Battery*kV__Motor*u1*np.pi*1.11e+2-N_s__Battery*R_s__Battery*u1*u2*x3*9.0e+3-N_p__Battery*N_s__Battery*Rm__Motor*kV__Motor*u1*np.pi*7.4e+2)*-3.0e+2)/(kV__Motor*np.pi*(N_p__Battery*9.0e+2+N_p__Battery*Rm__Motor*1.2e+4+N_p__Battery*Rm__Motor**2*4.0e+4+N_p__Battery*u1**2*2.7e+1+N_p__Battery*u2**2*2.7e+1+N_s__Battery*R_s__Battery*u1**2*9.0e+3+N_s__Battery*R_s__Battery*u2**2*9.0e+3+N_p__Battery*Rm__Motor*u1**2*1.8e+2+N_p__Battery*Rm__Motor*u2**2*1.8e+2+N_s__Battery*R_s__Battery*Rm__Motor*u1**2*6.0e+4+N_s__Battery*R_s__Battery*Rm__Motor*u2**2*6.0e+4)),et7*et8];
	mt4 = [((N_p__Battery*x3*9.0e+2+N_p__Battery*Rm__Motor*x3*6.0e+3+N_p__Battery*u1**2*x3*2.7e+1-N_p__Battery*u1*u2*x2*2.7e+1+N_s__Battery*R_s__Battery*u1**2*x3*9.0e+3-N_p__Battery*N_s__Battery*kV__Motor*u2*np.pi*1.11e+2-N_s__Battery*R_s__Battery*u1*u2*x2*9.0e+3-N_p__Battery*N_s__Battery*Rm__Motor*kV__Motor*u2*np.pi*7.4e+2)*-3.0e+2)/(kV__Motor*np.pi*(N_p__Battery*9.0e+2+N_p__Battery*Rm__Motor*1.2e+4+N_p__Battery*Rm__Motor**2*4.0e+4+N_p__Battery*u1**2*2.7e+1+N_p__Battery*u2**2*2.7e+1+N_s__Battery*R_s__Battery*u1**2*9.0e+3+N_s__Battery*R_s__Battery*u2**2*9.0e+3+N_p__Battery*Rm__Motor*u1**2*1.8e+2+N_p__Battery*Rm__Motor*u2**2*1.8e+2+N_s__Battery*R_s__Battery*Rm__Motor*u1**2*6.0e+4+N_s__Battery*R_s__Battery*Rm__Motor*u2**2*6.0e+4)),et5*et6];
	mt5 = [et3*et4,et1*et2,K_T__Propeller*x2**2,K_Q__Propeller*x2**2,K_T__Propeller*x3**2,K_Q__Propeller*x3**2];
	out = np.concatenate([mt1,mt2,mt3,mt4,mt5]);
	out_temp = [];
	for i in range(nn):
		l = [out[j,i] for j in range(15)]
		l=np.reshape(l, (15,1))
		out_temp.append(l)
	out = out_temp

	return out