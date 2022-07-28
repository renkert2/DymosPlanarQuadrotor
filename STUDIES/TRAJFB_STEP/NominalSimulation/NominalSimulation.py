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

init.init_output(__file__, dirname="Output")

traj = T.Step(tx=dm.GaussLobatto(num_segments=50, compressed=True), include_controller=True, sim_mode=True)
traj.x_des=0

cons = C.ConstraintSet() # Create an empty constraint set
#cons.add(C.BatteryCurrent()) # for multiple phases
#cons.add(C.InverterCurrent())
model = ps.PlanarSystemModel(traj, cons=cons)


#%% Baseline Controller Tuning
params = model._params

params["k_p_omega"].val = 0.000001
params["k_i_omega"].val = 0

params["k_d_r"].val = 0.01

#%%
rec = R.Recorder(name="nominal_sim_cases.sql")
prob = P.Problem(model=model, traj = traj, planar_recorder=rec)
prob.driver.options["maxiter"] = 1500

prob.setup()
#model.traj.phases.phase0.nonlinear_solver.options["maxiter"] = 1000
prob.init_vals()
prob.final_setup()


#%%
#prob.run_model()
om.n2(prob)

#%%
prob.record("nominal_sim_initial")
prob.run_driver()
prob.record("nominal_sim_final")

prob.cleanup_all()
