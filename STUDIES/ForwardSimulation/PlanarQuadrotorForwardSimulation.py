# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 08:36:58 2021

@author: renkert2
"""

import os
import PlanarSystem as ps
import dymos as dm
import openmdao.api as om
import time
import matplotlib.pyplot as plt
import SUPPORT_FUNCTIONS.plotting as my_plt # Just to get the default formatting
import SUPPORT_FUNCTIONS.init as init
import ProblemTemplates as PT


init.init_output(__file__)

#%%
prob = PT.ForwardSimulation()

# Run the Simulation Problem
tic = time.perf_counter()
prob.run_model()
toc = time.perf_counter()
run_time = toc-tic

print(f"Problem solved in {run_time:0.4f} seconds")

traj = prob.model.traj
sim_out = traj.simulate(times_per_seg=50)
t_sim = sim_out.get_val('traj.phase0.timeseries.time')

#%% Plots

# Powertrain States
states = ["PT_x1", "PT_x2", "PT_x3"]
labels = ["$q$", r"$\omega_1$ (rad/s)", r"$\omega_2$ (rad/s)"]
fig, axes = plt.subplots(len(states), 1)
fig.suptitle(r"\textbf{PowerTrain States}", fontweight='bold')
for i, state in enumerate(states):
    sim = axes[i].plot(t_sim, sim_out.get_val(f'traj.phase0.timeseries.states:{state}'), '-')
    axes[i].set_ylabel(labels[i])
axes[-1].set_xlabel('time (s)')
plt.tight_layout()
plt.savefig('FowardSimulation_PTStates.png')
plt.show()

# Body States
states = ['BM_x', 'BM_y', 'BM_theta']
labels = ['$x$ (m)', '$y$ (m)', r'$\theta$ (rad)']
fig, axes = plt.subplots(len(states), 1)
fig.suptitle(r"\textbf{Body States}", fontweight='bold')
for i, state in enumerate(states):
    sim = axes[i].plot(t_sim, sim_out.get_val(f'traj.phase0.timeseries.states:{state}'), '-')
    axes[i].set_ylabel(labels[i])
axes[-1].set_xlabel('time (s)')
plt.tight_layout()
plt.savefig('FowardSimulation_BodyStates.png')
plt.show()

# inputs = ['PT_u1', 'PT_u2']
# labels = ["u1", "u2"]
# fig, axes = plt.subplots(len(inputs), 1)
# fig.suptitle("Inputs")
# for i, input in enumerate(inputs):
#     sim = axes[i].plot(t_sim, sim_out.get_val(f'traj.phase0.timeseries.controls:{input}'), '-')
#     axes[i].set_ylabel(labels[i])
# axes[-1].set_xlabel('time (s)')
# plt.tight_layout()
# plt.show()

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
