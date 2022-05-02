# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 08:36:58 2021

@author: renkert2
"""
#%%
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
model = ps.PlanarSystemDesignModel(traj, opt_comps={"Battery":[], "PMSMMotor":[], "Propeller":[]})
rec = R.Recorder(name="sys_opt_cases.sql")
prob = P.Problem(model=model, traj = traj, planar_recorder=rec)
prob.setup()
prob.init_vals()

#%% Initialize from Input Optimization
reader = om.CaseReader(os.path.join(init.INPUT_OPT_PATH, "input_opt_cases.sql"))
input_opt_final = reader.get_case("input_opt_final")
prob.load_case(input_opt_final)

#%%
# Can also try trust-const algorithm
prob.driver.options["maxiter"] = 1000

prob.run("sys_opt")
om.n2(prob, outfile = "sys_opt_n2.html")
prob.cleanup()

#%% Save Optimal Parameter Values
import Param
import pickle

params = prob.model._params
des_params = Param.ParamSet([p for p in params if p.opt])
pv_opt = des_params.export_vals()

with open("pv_opt.pickle", 'wb') as f:
    pickle.dump(pv_opt, f)
