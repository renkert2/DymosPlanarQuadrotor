# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 08:36:58 2021

@author: renkert2
"""

import os
os.chdir(os.path.join(os.path.dirname(__file__), '..', '..'))
import PlanarSystem as ps
import dymos as dm
import openmdao.api as om
import time
import SUPPORT_FUNCTIONS.plotting as my_plt
import matplotlib.pyplot as plt
import warnings
import numpy as np
import pickle
import copy
import SUPPORT_FUNCTIONS.slugify as slug

os.chdir(os.path.dirname(__file__))
if not os.path.isdir("Output_ForwardSim"):
    os.mkdir("Output_ForwardSim")
os.chdir("Output_ForwardSim")

warnings.filterwarnings('ignore', category=om.UnitsWarning)

#%%
# Set up Desired Final Location:
x_init=0
y_init=0    

x_des = 10
y_des = 10

def pos_margin(p, margin):
    # Takes a list of positions and returns the min and the max with a padded boundary
    p_max = max(p)
    p_min = min(p)
    d = margin*(p_max - p_min)
    return (p_min - d, p_max + d)

(x_lb, x_ub) = pos_margin([x_init, x_des], 0.1)
(y_lb, y_ub) = pos_margin([y_init, y_des], 0.1)

#%%
nn = 25
tx = dm.GaussLobatto(num_segments=nn, solve_segments='forward')
phase = ps.PlanarSystemDynamicPhase(transcription=tx)
phase.init_vars()

# Set up States and Inputs as Optimization Variables
phase.set_time_options(fix_initial=True, fix_duration=True, duration_val=5, duration_ref0=0, duration_ref=5)

phase.set_state_options("PT_x1", val=1, lower=0, upper=1, fix_initial=True, ref0 = 0, ref=1) # Fix Battery State of Charge Initial State to 1
phase.set_state_options("PT_x2", fix_initial=True) # Scaling ref=5000 has the largest impact on the solution
phase.set_state_options("PT_x3", fix_initial=True) # Scaling ref=5000 has the largest impact on the solution
phase.set_state_options('BM_v_x', fix_initial=True)
phase.set_state_options('BM_v_y', fix_initial=True)
phase.set_state_options('BM_x', fix_initial=True)
phase.set_state_options('BM_y', fix_initial=True)
phase.set_state_options('BM_omega', fix_initial=True)
phase.set_state_options('BM_theta', fix_initial=True)

phase.set_control_options("PT_u1", lower=0, upper=1, opt=False, ref0=0.0, ref=1)
phase.set_control_options("PT_u2", lower=0, upper=1, opt=False, ref0=0.0, ref=1)

# Minimize time at the end of the phase
phase.add_objective('time', loc='final')
traj = dm.Trajectory()
traj.add_phase('phase0', phase)
meta = phase.Metadata

planar_model=ps.PlanarSystemModel(traj, meta, IncludeSurrogates=[], IncludeStaticModel=True)

prob = om.Problem(model=planar_model)
prob.driver = om.ScipyOptimizeDriver()
recorder = om.SqliteRecorder('cases.sql', record_viewer_data=False)
prob.add_recorder(recorder)
prob.recording_options['record_desvars'] = True
prob.recording_options['record_responses'] = True
prob.recording_options['record_objectives'] = True
prob.recording_options['record_constraints'] = True
prob.recording_options['record_inputs'] = True
prob.recording_options['includes'] = ["*"]

prob.setup()

# Set Initial Values
prob.set_val('traj.phase0.controls:PT_u1', 1)
prob.set_val('traj.phase0.controls:PT_u2', 1)

prob.set_val('traj.phase0.states:PT_x1', 1.0)
prob.set_val('traj.phase0.states:PT_x2', phase.interp('PT_x2', ys=(0,0)))
prob.set_val('traj.phase0.states:PT_x3', phase.interp('PT_x3', ys=(0,0)))
prob.set_val('traj.phase0.states:BM_v_x', phase.interp('BM_v_x', ys=[0, 0]))
prob.set_val('traj.phase0.states:BM_v_y', phase.interp('BM_v_y', ys=[0, 0]))
prob.set_val('traj.phase0.states:BM_x', phase.interp('BM_x', ys=[0, 0]))
prob.set_val('traj.phase0.states:BM_y', phase.interp('BM_y', ys=[0, 0]))
prob.set_val('traj.phase0.states:BM_omega', phase.interp('BM_omega', ys=[0, 0]))
prob.set_val('traj.phase0.states:BM_theta', phase.interp('BM_theta', ys=[0, 0]))

# Parameter Values
# set the battery mass to 0 initially
prob.set_val('traj.phase0.parameters:PT_theta16', 0)

prob.final_setup()

#%%
#
# Run the Optimization Problem for Various Masses
#
# mass_vals = np.arange(0.0, 2.1, 0.1)
mass_vals = [0.9, 1.0, 1.1]
sims = []
for (i,val) in enumerate(mass_vals):
    prob.set_val('traj.phase0.parameters:PT_theta16', val)
    print(f"Solving forward simulation for mass {val}")
    prob.run_model()
    prob.record(f'final_massval_{i}')
    sim_out = traj.simulate(times_per_seg=50)
    sims.append(sim_out)
prob.cleanup()


# Get the final value of the design variable

#%% Plots
# plt.subplots(sim_out, prob, path='traj.phase0.timeseries',
#              vars=[f"states:{x}" for x in  ['BM_x', 'BM_y', 'BM_theta']] + [f"controls:{x}" for x in  ['PT_u1', 'PT_u2']],
#              labels=['$x$', '$y$', r'$\theta$', "$u_1$", "$u_2$"], 
#              title="Planar Quadrotor Input Optimization", save=True)
cr = om.CaseReader('cases.sql')
prob_cases = cr.get_cases('problem', recurse=False)

path='traj.phase0.timeseries'
vars=[f"states:{x}" for x in  ['BM_x', 'BM_y', 'BM_theta']]
labels=['$x$', '$y$', r'$\theta$', "$u_1$", "$u_2$"]
title="Planar Quadrotor Forward Simulation"

    
fig, axes = plt.subplots(len(vars), 1, figsize=[5,6], dpi=300)

for i in range(len(prob_cases)):
    t_sim = sims[i].get_val(f'{path}.time')
    t_prob = prob_cases[i].get_val(f'{path}.time')
    for j, var in enumerate(vars):
        axes[j].plot(t_sim, sims[i].get_val(f'{path}.{var}'), '-')
        #axes[j].plot(t_prob, prob_cases[i].get_val(f'{path}.{var}'), 'o')
        axes[j].set_ylabel(labels[j])
axes[-1].set_xlabel('time (s)')
plt.tight_layout()
fig.suptitle(r"\textbf{"+title+"}")
name = slug.slugify(title)
plt.savefig(f'{name}.png')
plt.show()

#%% Thrust Ratio Calculation
for case in prob_cases:
    print(f"Case: {case.name}")
    print("Thrust Ratio Component: ", case["thrust_ratio.TR"])
    print()
    print("--- Masses ---")
    masses = []
    for mass in ["Mass__Frame", "Mass__Battery", "Mass__Motor", "Mass__Motor", "Mass__Propeller",  "Mass__Propeller"]:
        mass_val = case[f'mass.{mass}']
        masses.append(mass_val)
        print(f"\t{mass}: {mass_val}")
    print("\tComponent Total Mass: ", case["mass.Mass__PlanarQuadrotor"])
    print("\tBodyModel Total Mass: ", case['traj.phases.phase0.timeseries.input_values:parameters:BM_m'][0])
    print("\tManually Calculated Mass: ", sum(masses))
    print()
    
