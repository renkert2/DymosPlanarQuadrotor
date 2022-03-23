# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 08:36:58 2021

@author: renkert2
"""

import openmdao.api as om
import SUPPORT_FUNCTIONS.init as init
import ProblemTemplates as PT
import Recorders as R
import Sweeps as sweep
import numpy as np

init.init_output(__file__)

prob = PT.StepProblem()

prob.setup()
prob.init_vals()

print("Running Model")
prob.run_model()
om.n2(prob)

#%%
sweep.simple_sweep(prob, "D__Propeller", np.linspace(0.1041, 0.6858, num=20))

#%%
prob.init_vals()
prob.run_model()
sweep.simple_sweep(prob, "P__Propeller", np.linspace(0.0762, 0.3810, num=20))






    
