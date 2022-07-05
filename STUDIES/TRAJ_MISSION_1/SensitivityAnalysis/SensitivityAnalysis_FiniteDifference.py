# -*- coding: utf-8 -*-
"""
Created on Fri Apr 15 10:52:57 2022

@author: renkert2
"""

import os
import time
import dymos as dm
import openmdao.api as om
import numpy as np

import SUPPORT_FUNCTIONS.init as init
import SUPPORT_FUNCTIONS.plotting as plotting
import SUPPORT_FUNCTIONS.support_funcs as funcs
import matplotlib.pyplot as plt
import Problems as P
import Recorders as R
import Trajectories as T
import PlanarSystem as ps
import Constraints as C

init.init_output(__file__)

# Load Optimal Input Case
input_opt_path = os.path.join(os.path.dirname(__file__), "..", "InputOptimization", "Output")
reader = om.CaseReader(os.path.join(input_opt_path, "input_opt_cases.sql"))
input_opt_final = reader.get_case("input_opt_final")

# Problem 1: No Solve Segments
traj = T.Mission_1()
cons = C.ConstraintSet() # Create an empty constraint set
#TODO: cons.add(C.BatteryCurrent()) for multiple phases
cons.add(C.InverterCurrent())
model = ps.PlanarSystemModel(traj, cons=cons)

prob = P.Problem(model=model, traj = traj, planar_recorder=None)
prob.driver.options["maxiter"] = 1000

prob.setup()
prob.init_vals()
prob.load_case(input_opt_final)

#%% Finite Differencing
surr = prob.planar_model.surrogates

ins = funcs.flatten([surr[x].inputs for x in ("Battery", "PMSMMotor", "Propeller")])
outs = funcs.flatten([surr[x].outputs for x in ("Battery", "PMSMMotor", "Propeller")])

objs = prob.model.get_objectives().keys()

(fd, lt) = prob.fdiff(of = objs, wrt = ins, step_size = 0.01)

#%%
for tbl in lt:
    print(lt[tbl])