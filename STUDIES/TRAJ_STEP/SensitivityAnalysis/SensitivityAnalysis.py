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

#rec = R.Recorder(name="sens_cases.sql")
prob = P.Problem(model=model, traj = traj, planar_recorder=None)

# Problem 2: Solve Segments
#traj_ss = T.Step(tx=dm.ExplicitShooting(num_segments=25, compressed=True, grid='gauss-lobatto'), sim_mode=True)
traj_ss = T.Step(tx=dm.GaussLobatto(num_segments=25, compressed=True, solve_segments="forward"), sim_mode=True)
#model_ss = ps.PlanarSystemModel(traj_ss)
#cons = C.ConstraintSet()
model_ss = ps.PlanarSystemModel(traj_ss)

#rec_ss = R.Recorder(name="sens_cases_ss.sql")
prob_ss = P.Problem(model = model_ss, traj = traj_ss, planar_recorder=None)

probs = [prob, prob_ss]

for p,n in zip(probs, ["sens_n2.html", "sens_n2_ss.html"]):
    p.setup()
    p.init_vals()
    p.final_setup()
    om.n2(p, outfile=n)

#%% Convergence
# What exactly converges / is solved when we just run "run_model"?

for p,n in zip([prob, prob_ss], ["solve\_segments=False", "solve\_segments='forward'"]):
    p.init_vals()
    
    # TODO: Interpolate and use finer grid for traj_ss
    #p.set_val('traj.phase0.controls:PT_u1', input_opt_final.get_val("traj.phase0.controls:PT_u1"))
    #p.set_val('traj.phase0.controls:PT_u2', input_opt_final.get_val("traj.phase0.controls:PT_u2"))
    
    nn_c = prob.traj.tx.grid_data.subset_num_nodes["control_input"]
    p.set_val('traj.phase0.controls:PT_u1', 0.855*np.ones((nn_c,)))
    p.set_val('traj.phase0.controls:PT_u2', 0.85*np.ones((nn_c,)))
    
    
    (fig, ax) = plt.subplots(nrows=2)
    fig.suptitle(f"Model Test: {n}")
    ax[0].set_ylabel("$x$ (m)")
    ax[1].set_ylabel("$y$ (m)")
    
    x=p.get_val('traj.phase0.states:BM_x')
    y=p.get_val('traj.phase0.states:BM_y')
    ax[0].plot(x, label="Pre-run")
    ax[1].plot(y, label="Pre-run")
    
    p.run_model()
    
    x=p.get_val('traj.phase0.states:BM_x')
    y=p.get_val('traj.phase0.states:BM_y')
    ax[0].plot(x, label="Post-run")
    ax[1].plot(y, label="Post-run")
    
    for a in ax:
        a.set_xlabel("node")
        a.legend()

#%%
# import my_plt
# my_plt.export(plt.figure(1), fname="mdl_test_solve_seg_false")
# my_plt.export(plt.figure(2), fname="mdl_test_solve_seg_forward")

#%% Load Optimal Vals
for p in probs:
    p.load_case(input_opt_final)
    p.run_model()

# Double check things line up correctly
plotting.timeseries_plots(probs, legend=['sens', "sens\_ss"])

#%% Computing Totals
param_paths = ["params."+x.strID for x in prob.model._params]
x = prob_ss.compute_totals(of=["traj.phases.phase0.time.time"], driver_scaling=True)
