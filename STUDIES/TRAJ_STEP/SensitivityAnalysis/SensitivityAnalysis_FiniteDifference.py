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
reader = om.CaseReader(os.path.join(init.INPUT_OPT_PATH, "input_opt_cases.sql"))
input_opt_final = reader.get_case("input_opt_final")


# Problem 1: No Solve Segments
traj = T.Step()
model = ps.PlanarSystemModel(traj)

prob = P.Problem(model=model, traj = traj, planar_recorder=None)

prob.setup()
prob.init_vals()

#%% Finite Differencing
surr = prob.planar_model.surrogates

ins = funcs.flatten([surr[x].inputs for x in ("Battery", "PMSMMotor", "Propeller")])
outs = funcs.flatten([surr[x].outputs for x in ("Battery", "PMSMMotor", "Propeller")])

objs = prob.model.get_objectives().keys()

(fd, lt) = prob.fdiff(of = objs, wrt = ins, step_size = 0.01)

#%%
for tbl in lt:
    print(lt[tbl])