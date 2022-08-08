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
import pickle

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

input_opt_path = os.path.join(init.HOME_PATH, "STUDIES", "TRAJ_STEP", "InputOptimization", "Output")
reader = om.CaseReader(os.path.join(input_opt_path, "input_opt_cases.sql"))
input_opt_final = reader.get_case("input_opt_final")

time, trajdat = T.getReferenceTraj(input_opt_final)
tx = dm.GaussLobatto(num_segments=20, compressed=True)
traj = T.Track(time, trajdat["x_T"], trajdat["y_T"], trajdat["v_x_T"], trajdat["v_y_T"], trajdat["a_x_T"], trajdat["a_y_T"], trajdat["theta_T"], trajdat["omega_T"], tx=tx)
cons = C.ConstraintSet() # Create an empty constraint set
#cons.add(C.BatteryCurrent()) # for multiple phases
#cons.add(C.InverterCurrent())
model = ps.PlanarSystemModel(traj, cons=cons)
params = model._params

#%%
rec = R.Recorder(name="gain_sweep_cases.sql")
prob = P.Problem(model=model, traj = traj, planar_recorder=rec)

prob.setup()
#model.traj.phases.phase0.nonlinear_solver.options["maxiter"] = 1000
prob.init_vals()
prob.final_setup()

#%% Nominal Controller
params["k_p_r"].val = 1
params["k_d_r"].val = 2
params["k_p_theta"].val = 0.3
params["k_d_theta"].val = 0.75

params["k_p_omega"].val = 0.003
params["k_i_omega"].val = 0.03
params["k_b_omega"].val = 1000

#%%
k_p_r_vals = np.arange(0.1,10,0.1)
for i,v in enumerate(k_p_r_vals):
    print(f"Evaluating Gain {i}: k_p_r={v}")
    params["k_p_r"].val=v
    prob.run_driver()
    prob.record(f"gain_sweep_{i}")
    obj = prob.get_objective()
    print(f"Objective Function Value: {obj}")


#%%
prob.cleanup_all()

