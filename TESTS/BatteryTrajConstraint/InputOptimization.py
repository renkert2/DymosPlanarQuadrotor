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
import OPTIM.Search as search
init.init_output(__file__)


traj = T.Mission_1(tx=dm.GaussLobatto(num_segments=5, compressed=True))
cons = C.ConstraintSet() # Create an empty constraint set
cons.add(C.BatteryCurrent())
cons.add(C.InverterCurrent())
model = ps.PlanarSystemModel(traj, cons=cons)

#%%
rec = R.Recorder(name="input_opt_cases.sql")
prob = P.Problem(model=model, traj = traj, planar_recorder=rec)
prob.driver.options["maxiter"] = 1000

prob.setup()
prob.init_vals()

#%% Load optimal configuration from discrete search

reader = search.SearchReader(output_dir = os.path.join(init.HOME_PATH, "STUDIES/TRAJ_MISSION_1/DiscreteSearch/Output_07052022/search_output/"))
opt_config = reader.result.opt_iter.config

pvals = opt_config.data

for p in model._params:
    pv = p.get_compatible(pvals)
    if pv:
        p.load_val(pv)
        p.dep=False
#%%
om.n2(prob)

#%%
prob.run("input_opt")

prob.cleanup_all()
