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

opt_path = os.path.join(init.HOME_PATH, "STUDIES", "TRAJFB_STEP", "TRAJFB_STEP_XY", "ControllerOptimization", "Output")
opt_reader_sim = om.CaseReader(os.path.join(opt_path, "controller_opt_cases_sim.sql"))
opt_case_sim = opt_reader_sim.get_case("controller_opt_final_sim")
opt_reader = om.CaseReader(os.path.join(opt_path, "controller_opt_cases.sql"))
opt_case = opt_reader.get_case("controller_opt_final")

input_opt_path = os.path.join(init.HOME_PATH, "STUDIES", "TRAJ_STEP", "InputOptimization", "Output")
reader = om.CaseReader(os.path.join(input_opt_path, "input_opt_cases.sql"))
input_opt_final = reader.get_case("input_opt_final")

time, trajdat = T.getReferenceTraj(input_opt_final, phases=[f"phase{i}" for i in range(1)])
tx = dm.GaussLobatto(num_segments=30, compressed=True)
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
#prob.load_case(opt_case)

for k,var in [(1,"params.k_p_r__Controller"), (1,"params.k_d_r_x__Controller"), (1,"params.k_d_r_y__Controller"), (1,"params.k_p_theta__Controller"), (1.12,"params.k_d_theta__Controller"), (1,"params.k_p_omega__Controller"), (1,"params.k_b_omega__Controller"), (1,"params.k_i_omega__Controller")]:
    prob.set_val(var, k*opt_case[var])
prob.run_model()

#%%
path = "traj.phase0.timeseries."
save_states = (("x", path+"states:BM_x"), ("y", path+"states:BM_y"), ("theta", path+"states:BM_theta"))

sim_segments = list(range(10,150,50))
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
opt_time = opt_case.get_val(path+"time")
for i,ax in enumerate(axes):
    for res in results:
        ax.plot(res["time"], res[save_states[i][0]], label=f"TPS: {res['times_per_seg']}")
    
    ax.plot(opt_case_sim.get_val(path+"time"), opt_case_sim.get_val(save_states[i][1]), label="Opt Sim")
    ax.plot(opt_case.get_val(path+"time"), opt_case.get_val(save_states[i][1]), label="Opt Disc")
    ax.legend()

#%%
prob.cleanup_all()

