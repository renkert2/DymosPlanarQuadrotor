# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 08:36:58 2021

@author: renkert2
"""
import os
import openmdao.api as om
import SUPPORT_FUNCTIONS.init as init
import Problems as P
import Trajectories as T
import PlanarSystem as ps
import Recorders as R
import numpy as np
import Sweeps as sweep

init.init_output(__file__)
traj = T.Step()
model = ps.PlanarSystemSearchModel(traj)

prob = P.Problem(model=model, traj = traj, planar_recorder=None)

prob.setup()
prob.init_vals()

# Initialize from Input Optimization
reader = om.CaseReader(os.path.join(init.INPUT_OPT_PATH, "input_opt_cases.sql"))
input_opt_final = reader.get_case("input_opt_final")
prob.load_case(input_opt_final)

#%%
sweep.simple_sweep(prob, "D__Propeller", np.linspace(0.1041, 0.6858, num=20))

#%%
prob.init_vals()
prob.load_case(input_opt_final)
sweep.simple_sweep(prob, "P__Propeller", np.linspace(0.0762, 0.3810, num=20))






    
