# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 08:36:58 2021

@author: renkert2
"""
import os
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

input_opt_path = os.path.join(init.HOME_PATH, "STUDIES", "TRAJ_MISSION__1", "InputOptimization", "Output_20")
reader = om.CaseReader(os.path.join(input_opt_path, "input_opt_cases.sql"))
input_opt_final = reader.get_case("input_opt_final")

time, trajdat = T.getReferenceTraj(input_opt_final, phases=[f"phase{i}" for i in range(5)])
tx = dm.GaussLobatto(num_segments=20, compressed=True)
#tx = dm.Radau(num_segments=20, compressed=True)
traj = T.Track(time, trajdat["x_T"], trajdat["y_T"], trajdat["v_x_T"], trajdat["v_y_T"], trajdat["a_x_T"], trajdat["a_y_T"], trajdat["theta_T"], trajdat["omega_T"], tx=tx)
cons = C.ConstraintSet() # Create an empty constraint set
model = ps.PlanarSystemModel(traj, cons=cons)
params = model._params

#%%
rec = R.Recorder(name="sim_study_cases.sql")
prob = P.Problem(model=model, traj = traj, planar_recorder=rec)

prob.setup()
prob.init_vals()
prob.final_setup()

#%%
params["k_p_r"].val = 0
params["k_d_r_x"].val = 50
params["k_d_r_y"].val = 28
params["k_p_theta"].val = 0.57
params["k_d_theta"].val = 0.736

params["k_p_omega"].val = 0.003
params["k_i_omega"].val = 0.03
params["k_b_omega"].val = 1000

pv_ctrl = model.controller_params.export_vals()

with open("pv_ctrl.pickle", 'wb') as f:
    pickle.dump(pv_ctrl, f)

#%%
prob.run_model()

path = "traj.phase0.timeseries."
save_states = (("x", path+"states:BM_x"), ("y", path+"states:BM_y"), ("theta", path+"states:BM_theta"))

sim_segments = list(range(10,110,10))
results = []
for ss in sim_segments:
    sim_prob = T.SimProblem(prob.traj, times_per_seg=ss)
    sim_prob.setup()
    sim_prob.simulate()
    
    res = {}
    res["times_per_seg"] = ss
    res["time"] = sim_prob.get_val(path+"time")
    
    # Get Data
    for n, p in save_states:
        res[n] = sim_prob.get_val(p)
    
    results.append(res)
        
with open("times_per_seg_sweep.pickle", 'wb') as f:
    pickle.dump(results, f)
    
#%%
(fig, axes) = plt.subplots(3,1)

for i,ax in enumerate(axes):
    for res in results:
        ax.plot(res["time"], res[save_states[i][0]], label=f"TPS: {res['times_per_seg']}")

    ax.legend()

#%%
prob.cleanup_all()

