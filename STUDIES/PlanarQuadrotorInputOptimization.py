# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 08:36:58 2021

@author: renkert2
"""

import os
os.chdir('..')
import PlanarSystem as ps
import dymos as dm
import openmdao.api as om
import matplotlib.pyplot as plt
import time

nn = 20
tx = dm.Radau(num_segments=nn, compressed=False)
phase = ps.PlanarSystemPhase(tx)

# Set up States and Inputs as Optimization Variables
phase.set_time_options(fix_initial=True, initial_val=0, duration_bounds=(0.001, 50))

phase.set_state_options("PT_x1", val=1, lower=0, upper=1, fix_initial=True, ref0 = 0, ref=1) # Fix Battery State of Charge Initial State to 1
phase.set_state_options("PT_x2", fix_initial=True, lower=0, upper=5000, ref0=0.0, ref=5000) # Scaling ref=5000 has the largest impact on the solution
phase.set_state_options("PT_x3", fix_initial=True, lower=0, upper=5000, ref0=0.0, ref=5000) # Scaling ref=5000 has the largest impact on the solution
phase.set_state_options('BM_v_x', fix_initial=True, fix_final=True)
phase.set_state_options('BM_v_y', fix_initial=True, fix_final=True)
phase.set_state_options('BM_x', fix_initial=True, fix_final=True)
phase.set_state_options('BM_y', fix_initial=True, fix_final=True)
phase.set_state_options('BM_omega', fix_initial=True, fix_final=True)
phase.set_state_options('BM_theta', fix_initial=True, fix_final=True)

phase.set_control_options("PT_u1", lower=0, upper=1, opt=True, ref0=0.0, ref=1)
phase.set_control_options("PT_u2", lower=0, upper=1, opt=True, ref0=0.0, ref=1)

phase.add_boundary_constraint('PT.x2_dot', loc='final', shape=(1,), equals=0) # Shape may need to change to (nn,)
phase.add_boundary_constraint('PT.x3_dot', loc='final', shape=(1,), equals=0)
phase.add_boundary_constraint('BM.v_y_dot', loc='final', shape=(1,), equals=0, units='m/s**2')
phase.add_boundary_constraint('BM.omega_dot', loc='final', shape=(1,), equals=0, units='rad/s**2')

# Minimize time at the end of the phase
phase.add_objective('time', loc='final')

prob = om.Problem(model=om.Group())
prob.driver = om.ScipyOptimizeDriver()
traj = dm.Trajectory()
traj.add_phase('phase0', phase)

prob.model.add_subsystem('traj', traj)
prob.model.linear_solver = om.DirectSolver() # I'm not sure why we need this

prob.setup()

#%%
# Set Initial Values
prob.set_val('traj.phase0.t_initial', 0.0)
prob.set_val('traj.phase0.t_duration', 10.0)

prob.set_val('traj.phase0.controls:PT_u1', 0.5)
prob.set_val('traj.phase0.controls:PT_u2', 0.5)

prob.set_val('traj.phase0.states:PT_x1', 1.0)
prob.set_val('traj.phase0.states:PT_x2', phase.interp('PT_x2', ys=(0,1000)))
prob.set_val('traj.phase0.states:PT_x3', phase.interp('PT_x3', ys=(0,1000)))
prob.set_val('traj.phase0.states:BM_v_x', phase.interp('BM_v_x', ys=[0, 0]))
prob.set_val('traj.phase0.states:BM_v_y', phase.interp('BM_v_y', ys=[0, 0]))
prob.set_val('traj.phase0.states:BM_x', phase.interp('BM_x', ys=[0, 10]))
prob.set_val('traj.phase0.states:BM_y', phase.interp('BM_y', ys=[0, 10]))
prob.set_val('traj.phase0.states:BM_omega', phase.interp('BM_omega', ys=[0, 0]))
prob.set_val('traj.phase0.states:BM_theta', phase.interp('BM_theta', ys=[0, 0]))


#
# Run the Optimization Problem
#
tic = time.perf_counter()
dm.run_problem(prob)
toc = time.perf_counter()
run_time = toc-tic
print(f"Problem solved in {run_time:0.4f} seconds")

sim_out = traj.simulate(times_per_seg=50)

t_sol = prob.get_val('traj.phase0.timeseries.time')
t_sim = sim_out.get_val('traj.phase0.timeseries.time')

#%% Plots

# Powertrain States
states = ["PT_x1", "PT_x2", "PT_x3"]
labels = ["q", "omega_1", "omega_2"]
fig, axes = plt.subplots(len(states), 1)
for i, state in enumerate(states):
    sol = axes[i].plot(t_sol, prob.get_val(f'traj.phase0.timeseries.states:{state}'), 'o')
    sim = axes[i].plot(t_sim, sim_out.get_val(f'traj.phase0.timeseries.states:{state}'), '-')
    axes[i].set_ylabel(labels[i])
axes[-1].set_xlabel('time (s)')
plt.tight_layout()
plt.show()

# Body States
states = ['BM_x', 'BM_y', 'BM_theta']
labels = ['x', 'y', 'theta']
fig, axes = plt.subplots(len(states), 1)
for i, state in enumerate(states):
    sol = axes[i].plot(t_sol, prob.get_val(f'traj.phase0.timeseries.states:{state}'), 'o')
    sim = axes[i].plot(t_sim, sim_out.get_val(f'traj.phase0.timeseries.states:{state}'), '-')
    axes[i].set_ylabel(labels[i])
axes[-1].set_xlabel('time (s)')
plt.tight_layout()
plt.show()

inputs = ['PT_u1', 'PT_u2']
labels = ["u1", "u2"]
fig, axes = plt.subplots(len(inputs), 1)
for i, input in enumerate(inputs):
    sol = axes[i].plot(t_sol, prob.get_val(f'traj.phase0.timeseries.controls:{input}'), 'o')
    sim = axes[i].plot(t_sim, sim_out.get_val(f'traj.phase0.timeseries.controls:{input}'), '-')
    axes[i].set_ylabel(labels[i])
axes[-1].set_xlabel('time (s)')
plt.tight_layout()
plt.show()

# outputs = ["y12", "y13", "y14", "y15"]
# labels = ["Thrust 1", "Torque 1", "Thrust 2", "Torque 2"]
# fig, axes = plt.subplots(len(outputs), 1)
# for i, output in enumerate(outputs):
#     sol = axes[i].plot(t_sol, prob.get_val(f'traj.phase0.timeseries.outputs:{output}'), 'o')
#     sim = axes[i].plot(t_sim, sim_out.get_val(f'traj.phase0.timeseries.outputs:{output}'), '-')
#     axes[i].set_ylabel(labels[i])
# axes[-1].set_xlabel('time (s)')
# plt.tight_layout()
# plt.show()
