# -*- coding: utf-8 -*-
"""
Created on Tue Nov  9 09:46:28 2021

@author: renkert2
"""

import sys
import os
import numpy as np
os.chdir(r'C:/Users/renkert2/Documents/ARG_Research/DymosPlanarQuadrotor')
sys.path.append('PlanarPowerTrainModel')
print(os.getcwd())
print(sys.path)

#%%
from Model_f import Calc_f
from Model_g import Calc_g
from ModelJ_g_theta import CalcJ_g_theta

nn = 10;

# Set up Test Vectors: 3,2,8,21
x = np.tile(range(nn), (3,1))
u = np.tile(range(nn), (2,1))
d = np.tile(range(nn), (8,1))
theta = np.tile(range(nn), (21,1))
#%%
# Call the function
x_dot = Calc_f(x,u,d,theta, nn)
y = Calc_g(x,u,d,theta, nn)
# Parse the outputs
