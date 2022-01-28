# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 08:36:58 2021

@author: renkert2
"""

import os
os.chdir(os.path.join(os.path.dirname(__file__), '..', '..'))
import PlanarSystem as ps
import dymos as dm
import openmdao.api as om
import time
import SUPPORT_FUNCTIONS.plotting as my_plt
import matplotlib.pyplot as plt
import warnings
import numpy as np
import pickle
import copy

os.chdir(os.path.dirname(__file__))
if not os.path.isdir("Output_MassStudyOptiFail"):
    os.mkdir("Output_MassStudyOptiFail")
os.chdir("Output_MassStudyOptiFail")

#%% Convergence

cr = om.CaseReader('cases_1.sql')
my_plt.iterplots(cr, ['traj.phase0.t_duration'],labels=["Minimum Time (s)"], title="Minimum Time Iterations", save=False)

#%%
driver_cases = cr.get_cases('driver')

#%%
cr = om.CaseReader('cases_2_posscaling.sql')
driver_cases = cr.get_cases('driver')
prob_cases = cr.get_cases('problem')

#%%
cons = prob_cases[-1].get_constraints()