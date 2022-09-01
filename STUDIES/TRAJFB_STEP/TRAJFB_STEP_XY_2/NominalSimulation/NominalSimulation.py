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

# Just to get the default formatting
import SUPPORT_FUNCTIONS.plotting as my_plt
import matplotlib.pyplot as plt
import SUPPORT_FUNCTIONS.init as init
import SUPPORT_FUNCTIONS.timing as timing
import Constraints as C
import Problems as P
import Recorders as R
import Trajectories as T
import PlanarSystem as ps

init.init_output(__file__, dirname="Output")

tx = dm.GaussLobatto(num_segments=50, compressed=True)

traj = T.TrackStep(5, 10, 10, zero_initial=True, tx=tx)
cons = C.ConstraintSet()  # Create an empty constraint set

model = ps.PlanarSystemModel(traj, cons=cons)
params = model._params

# %%
rec = R.Recorder(name="nominal_sim_cases.sql")
prob = P.Problem(model=model, traj=traj, planar_recorder=rec)

prob.setup()
prob.init_vals()
prob.final_setup()

# %%
params["k_p_r"].val = 0
params["k_d_r_x"].val = 2
params["k_d_r_y"].val = 2
params["k_p_theta"].val = 0.3
params["k_d_theta"].val = 0.75

params["k_p_omega"].val = 0.003
params["k_i_omega"].val = 0.03
params["k_b_omega"].val = 1000

pv_ctrl = model.controller_params.export_vals()

with open("pv_ctrl.pickle", 'wb') as f:
    pickle.dump(pv_ctrl, f)

# %%
prob.run_driver()
prob.record("nominal_sim_final")

prob.sim_prob.simulate()
prob.sim_prob.record("nominal_sim_final_sim")

# %%
prob.cleanup_all()
