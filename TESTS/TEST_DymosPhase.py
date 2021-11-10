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
os.chdir('..')
sys.path.append(r'C:\Users\renkert2\Documents\ARG_Research\GraphTools\Dymos')
from DymosModel import DymosPhase



nn = 10
p = om.Problem(model = om.Group())
mdl = "PlanarPowerTrainModel"

tx = dm.Radau(num_segments=nn, compressed=True)
phase = DymosPhase(mdl, tx)

traj = dm.Trajectory()
traj.add_phase('phase0', phase)

prob = om.Problem(model=om.Group())
prob.model.add_subsystem('traj', traj)

prob.setup()
prob.set_val('traj.phase0.t_initial', 0.0)
prob.set_val('traj.phase0.t_duration', 2.0)

prob.set_val('traj.phase0.controls:u1', 1)
prob.set_val('traj.phase0.controls:u2', 1)

prob.run_model()
sim_out = traj.simulate(times_per_seg=50)

t_sol = prob.get_val('traj.phase0.timeseries.time')
t_sim = sim_out.get_val('traj.phase0.timeseries.time')

#%%
states = ['x1', 'x2', 'x3']
fig, axes = plt.subplots(len(states), 1)
for i, state in enumerate(states):
    sol = axes[i].plot(t_sol, prob.get_val(f'traj.phase0.timeseries.states:{state}'), 'o')
    sim = axes[i].plot(t_sim, sim_out.get_val(f'traj.phase0.timeseries.states:{state}'), '-')
    axes[i].set_ylabel(state)
axes[-1].set_xlabel('time (s)')
plt.tight_layout()
plt.show()

# inputs = ['u_1', 'u_2']
# fig, axes = plt.subplots(len(inputs), 1)
# for i, input in enumerate(inputs):
#     # sol = axes[i].plot(t_sol, prob.get_val(f'traj.phase0.timeseries.controls:{input}'), 'o')
#     sim = axes[i].plot(t_sim, sim_out.get_val(f'traj.phase0.timeseries.controls:{input}'), '-')
#     axes[i].set_ylabel(input)
# axes[-1].set_xlabel('time (s)')
# plt.tight_layout()
# plt.show()


#%%