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

import SUPPORT_FUNCTIONS.init as init
import Problems as P
import Recorders as R
import Trajectories as T
import PlanarSystem as ps

init.init_output(__file__)

traj = T.Step()
model = ps.PlanarSystemDesignModel(traj, opt_comps={"Battery":[]})
rec = R.Recorder(name="batt_opt_cases.sql")
prob = P.Problem(model=model, traj = traj, planar_recorder=rec)
prob.setup()
prob.init_vals()

#%% Initialize from Input Optimization
reader = om.CaseReader(os.path.join(init.INPUT_OPT_PATH, "input_opt_cases.sql"))
input_opt_final = reader.get_case("input_opt_final")
prob.load_case(input_opt_final)

#%%
prob.run("batt_opt")
om.n2(prob, outfile = "batt_opt_n2.html")
prob.cleanup()