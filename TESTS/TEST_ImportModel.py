# -*- coding: utf-8 -*-
"""
Created on Mon Nov  8 11:14:36 2021

@author: renkert2
"""
import sys
import os
os.chdir('..')
sys.path.append(r'C:\Users\renkert2\Documents\ARG_Research\GraphTools\Dymos')
from DymosModel import DymosModel
dm = DymosModel()

dm.ImportModel("PlanarPowerTrainModel")

#%%