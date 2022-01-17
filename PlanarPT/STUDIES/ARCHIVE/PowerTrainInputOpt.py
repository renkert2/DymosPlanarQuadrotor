# -*- coding: utf-8 -*-
"""
Created on Mon Nov  8 11:14:36 2021

@author: renkert2
"""
import sys
import os
import openmdao.api as om
import dymos as dm
import matplotlib.pyplot as plt
from DymosModel import DymosPhase
import numpy as np



nn = 20
mdl = "PlanarPowerTrainModel"

tx = dm.Radau(num_segments=nn, compressed=False)

mdl_path = 'C:/Users/renkert2/Documents/ARG_Research/DymosPlanarQuadrotor/PlanarPT' # Point Model to folder containing the Model folder.  This is required for !openmdao check functions
os.chdir('..')

phase = DymosPhase(mdl, tx, disturbance_opts={"val":0}, path=mdl_path, include_disturbances=False)
traj = dm.Trajectory()
traj.add_phase('phase0', phase)

# Set up States and Inputs as Optimization Variables
phase.set_time_options(fix_initial=True, initial_val=0, duration_bounds=(0.001, 3))

phase.set_state_options("x1", val=1, lower=0, upper=1, fix_initial=True, ref0 = 0, ref=1) # Fix Battery State of Charge Initial State to 1
phase.set_state_options("x2", fix_initial=True, fix_final=True, lower=0, upper=5000, ref0=0.0, ref=5000) # Scaling ref=5000 has the largest impact on the solution
phase.set_state_options("x3", fix_initial=True, fix_final=True, lower=0, upper=5000, ref0=0.0, ref=5000) # Scaling ref=5000 has the largest impact on the solution

phase.set_control_options("u1", lower=0, upper=1, opt=True, ref0=0.0, ref=1)
phase.set_control_options("u2", lower=0, upper=1, opt=True, ref0=0.0, ref=1)

phase.add_boundary_constraint('x2_dot', loc='final', shape=(1,), equals=0) # Shape may need to change to (nn,)
phase.add_boundary_constraint('x3_dot', loc='final', shape=(1,), equals=0)

# Minimize time at the end of the phase
phase.add_objective('time', loc='final')

prob = om.Problem(model=om.Group())
prob.driver = om.ScipyOptimizeDriver()
#prob.driver.declare_coloring(show_sparsity=True, num_full_jacs=3)
prob.model.add_subsystem('traj', traj)
prob.model.linear_solver = om.DirectSolver() # I'm not sure why we need this

prob.setup()

prob.set_val('traj.phase0.t_initial', 0.0)
prob.set_val('traj.phase0.t_duration', 1.0)

prob.set_val('traj.phase0.controls:u1', 0.5)
prob.set_val('traj.phase0.controls:u2', 0.5)

prob.set_val('traj.phase0.states:x1', 1.0)
prob.set_val('traj.phase0.states:x2', phase.interp('x2', ys=(0,1000)))
prob.set_val('traj.phase0.states:x3', phase.interp('x3', ys=(0,1000)))


#
# Run the Optimization Problem
#
dm.run_problem(prob)
sim_out = traj.simulate(times_per_seg=50)

t_sol = prob.get_val('traj.phase0.timeseries.time')
t_sim = sim_out.get_val('traj.phase0.timeseries.time')

#%%
states = ['x1', 'x2', 'x3']
labels = ['q', 'omega_1', 'omega_2']
fig, axes = plt.subplots(len(states), 1)
for i, state in enumerate(states):
    sol = axes[i].plot(t_sol, prob.get_val(f'traj.phase0.timeseries.states:{state}'), 'o')
    sim = axes[i].plot(t_sim, sim_out.get_val(f'traj.phase0.timeseries.states:{state}'), '-')
    axes[i].set_ylabel(labels[i])
axes[-1].set_xlabel('time (s)')
plt.tight_layout()
plt.show()

inputs = ['u1', 'u2']
fig, axes = plt.subplots(len(inputs), 1)
for i, input in enumerate(inputs):
    sol = axes[i].plot(t_sol, prob.get_val(f'traj.phase0.timeseries.controls:{input}'), 'o')
    sim = axes[i].plot(t_sim, sim_out.get_val(f'traj.phase0.timeseries.controls:{input}'), '-')
    axes[i].set_ylabel(input)
axes[-1].set_xlabel('time (s)')
plt.tight_layout()
plt.show()

outputs = ["y12", "y13", "y14", "y15"]
labels = ["Thrust 1", "Torque 1", "Thrust 2", "Torque 2"]
fig, axes = plt.subplots(len(outputs), 1)
for i, output in enumerate(outputs):
    sol = axes[i].plot(t_sol, prob.get_val(f'traj.phase0.timeseries.outputs:{output}'), 'o')
    sim = axes[i].plot(t_sim, sim_out.get_val(f'traj.phase0.timeseries.outputs:{output}'), '-')
    axes[i].set_ylabel(labels[i])
axes[-1].set_xlabel('time (s)')
plt.tight_layout()
plt.show()



#%%