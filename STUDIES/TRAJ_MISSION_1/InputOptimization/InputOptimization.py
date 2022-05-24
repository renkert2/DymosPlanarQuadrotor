# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 08:36:58 2021

@author: renkert2
"""
import os
import time
import dymos as dm
import openmdao.api as om
import numpy as np

import SUPPORT_FUNCTIONS.plotting as my_plt # Just to get the default formatting
import matplotlib.pyplot as plt
import SUPPORT_FUNCTIONS.init as init
import SUPPORT_FUNCTIONS.timing as timing
import Constraints as C
import Problems as P
import Recorders as R
import Trajectories as T
import PlanarSystem as ps
init.init_output(__file__)

warm_start = False

traj = T.Mission_1()
cons = C.ConstraintSet() # Create an empty constraint set
#TODO: cons.add(C.BatteryCurrent()) for multiple phases
cons.add(C.InverterCurrent())
model = ps.PlanarSystemModel(traj, cons=cons)

if warm_start:
    reader = om.CaseReader("input_opt_cases.sql")
    cases = reader.get_cases("problem")
    warm_case = cases[-1]
#%%
rec = R.Recorder(name="input_opt_cases.sql")
prob = P.Problem(model=model, traj = traj, planar_recorder=rec)
prob.driver.options["maxiter"] = 5000

prob.setup()
prob.init_vals()
if warm_start:
    prob.load_case(warm_case)

#%%
prob.run("input_opt")

prob.cleanup_all()
