# -*- coding: utf-8 -*-
"""
Created on Tue Nov  9 15:34:04 2021

@author: renkert2
"""
import sys
import os
import numpy as np
os.chdir(r'C:/Users/renkert2/Documents/ARG_Research/DymosPlanarQuadrotor')
sys.path.append('PlanarPowerTrainModel')
print(os.getcwd())
print(sys.path)
import matlab.engine
eng = matlab.engine.start_matlab()
#%%
eng.cd(r'C:/Users/renkert2/Documents/ARG_Research/DymosPlanarQuadrotor/PlanarPowerTrainModel')

#%%
out = eng.isprime(2+2)

x = np.reshape(range(3), (3,1)).tolist()
u = np.reshape(range(2), (2,1)).tolist()
d = np.reshape(range(8), (8,1)).tolist()
theta = np.reshape(range(21), (21,1)).tolist()

x = matlab.double(x);
u = matlab.double(u);
d = matlab.double(d);
theta = matlab.double(theta);

out = eng.Model_f(x,u,d,theta)

x_dot = eng.Model_f(x,u,d,theta)
y = eng.Model_g(x,u,d,theta)
J_g_theta = eng.ModelJ_g_theta(x,u,d,theta)