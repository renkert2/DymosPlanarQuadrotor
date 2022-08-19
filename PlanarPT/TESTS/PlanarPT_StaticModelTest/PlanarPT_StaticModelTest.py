# -*- coding: utf-8 -*-
"""
Created on Fri Mar 11 11:53:42 2022

@author: renkert2
"""

import os
import sys
import dymos as dm
import openmdao.api as om
import time
import matplotlib.pyplot as plt
import logging

from GraphTools_Phil_V2.OpenMDAO import Param as P

import SUPPORT_FUNCTIONS.plotting as my_plt # Just to get the default formatting
import SUPPORT_FUNCTIONS.init as init
import PlanarPT.PlanarPTModels as ppt

init.init_output(__file__)
    
logging.basicConfig(level=logging.INFO)

#%%
nn = 20
tx = dm.GaussLobatto(num_segments=nn, solve_segments='forward')

# Phase
phase = ppt.PlanarPTDynamicPhase(transcription=tx)
phase.init_vars()

phase.set_time_options(fix_initial=True, fix_duration=True, initial_val=0, duration_val=5)

phase.set_state_options("x1", val=1, lower=0, upper=1, fix_initial=True, ref0 = 0, ref=1) # Fix Battery State of Charge Initial State to 1
phase.set_state_options("x2", fix_initial=True, fix_final=False, lower=0, upper=5000, ref0=0.0, ref=5000) # Scaling ref=5000 has the largest impact on the solution
phase.set_state_options("x3", fix_initial=True, fix_final=False, lower=0, upper=5000, ref0=0.0, ref=5000) # Scaling ref=5000 has the largest impact on the solution

phase.set_control_options("u1", val=1, opt=False)
phase.set_control_options("u2", val=1, opt=False)

# Trajectory
traj = ppt.PlanarPTDynamicTraj(phase)
traj.init_vars()

# Parameters
ps = ppt.PlanarPTParams()
for p in ps:
    if p.parent == "Propeller":
        p.dep = False
pg = P.ParamGroup(param_set = ps)

# System
sys = P.ParamSystem(pg)
sys.add_subsystem("traj", traj)

# Static System
static = ppt.PlanarPTModelStatic()
sys.add_subsystem("static", static)

prob = om.Problem(model=sys)
prob.driver = om.ScipyOptimizeDriver()
prob.model.linear_solver = om.DirectSolver() # I'm not sure why we need this

prob.setup()

#%%
# Set Initial Values
prob.set_val('traj.phase0.t_initial', 0.0)
prob.set_val('traj.phase0.t_duration', 5.0)

prob.set_val('traj.phase0.controls:u1', 1)
prob.set_val('traj.phase0.controls:u2', 1)

prob.set_val('traj.phase0.states:x1', 1.0)
prob.set_val('traj.phase0.states:x2', phase.interp('x2', ys=(0,1000)))
prob.set_val('traj.phase0.states:x3', phase.interp('x3', ys=(0,1000)))


#
# Run the Model Problem
#
tic = time.perf_counter()
prob.run_model()
toc = time.perf_counter()
run_time = toc-tic

# Generate N2 Diagram
om.n2(prob, outfile="n2_PlanatPT_StaticModelTest.html")

print(f"Problem solved in {run_time:0.4f} seconds")

sim_out = traj.simulate(times_per_seg=50)
t_sim = sim_out.get_val('traj.phase0.timeseries.time')

#%% Plots

# Powertrain Total Thrust
left_thrust = sim_out.get_val(f'traj.phase0.timeseries.outputs:y1')
right_thrust = sim_out.get_val(f'traj.phase0.timeseries.outputs:y3')
total_thrust_dynamic = left_thrust + right_thrust

# Simple Model total thrust
total_thrust_static = prob.get_val('static.y1')

fig, axes = plt.subplots(1, 1)
fig.suptitle(r"Thrust Output: Static vs. Dynamic Model", fontweight='bold')

axes.plot(t_sim, total_thrust_dynamic, '-', label='Dynamic')
axes.axhline(y=total_thrust_static, color='r', linestyle='-', label='Static')

axes.set_ylabel("Total Thrust (N)")
axes.legend()

axes.set_xlabel('time (s)')
plt.tight_layout()
plt.savefig('FowardSimulation_PTStates.png')
plt.show()
