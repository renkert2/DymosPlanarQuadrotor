# -*- coding: utf-8 -*-
"""
Created on Mon Nov  8 11:14:36 2021

@author: renkert2
"""
import sys
import os
os.chdir('..')
from DymosModel import DymosModel
dm = DymosModel()

dm.ImportModel("PlanarPowerTrainModel")

#%%