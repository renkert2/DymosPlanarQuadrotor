# -*- coding: utf-8 -*-
"""
Created on Tue Nov  9 10:35:28 2021

@author: renkert2
"""
#%%
import numpy as np
m = np.array([[1,2,3], [4,5,6], [7,8,9], [10,11,12]])

out = [];
for i in range(3):
    # Get the value of each element corresponding to that time
    l = [m[j,i] for j in range(4)]
    l = np.reshape(l, (2,2))
    out.append(l)
    
out_arr = np.array(out)
