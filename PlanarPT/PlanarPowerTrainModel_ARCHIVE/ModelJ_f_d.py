import math
import numpy as np

def CalcJ_f_d(x,u,d,theta,nn):
# auto-generated function from matlab
	out = np.concatenate([0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]);
	out_temp = [];
	for i in range(nn):
		l = [out[j,i] for j in range(24)]
		l=np.reshape(l, (3,8))
		out_temp.append(l)
	out = out_temp

	return out