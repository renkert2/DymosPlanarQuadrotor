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
import SUPPORT_FUNCTIONS.plotting # Just to get the default formatting
import matplotlib.pyplot as plt
import warnings
import numpy as np
import pickle
import copy

os.chdir(os.path.dirname(__file__))
if not os.path.isdir("Output_MassSweep"):
    os.mkdir("Output_MassSweep")
os.chdir("Output_MassSweep")

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
nn = 20
tx = dm.GaussLobatto(num_segments=nn)
phase = ps.PlanarSystemDynamicPhase(transcription=tx)
phase.init_vars()


# Set up States and Inputs as Optimization Variables
phase.set_time_options(fix_initial=True, initial_val=0, duration_bounds=(1, 20), duration_ref0=1, duration_ref=20)

phase.set_state_options("PT_x1", val=1, lower=0, upper=1, fix_initial=True, ref0 = 0, ref=1) # Fix Battery State of Charge Initial State to 1
phase.set_state_options("PT_x2", fix_initial=True, lower=0, upper=5000, ref0=0.0, ref=5000) # Scaling ref=5000 has the largest impact on the solution
phase.set_state_options("PT_x3", fix_initial=True, lower=0, upper=5000, ref0=0.0, ref=5000) # Scaling ref=5000 has the largest impact on the solution
phase.set_state_options('BM_v_x', fix_initial=True, fix_final=True)
phase.set_state_options('BM_v_y', fix_initial=True, fix_final=True)
phase.set_state_options('BM_x', fix_initial=True, fix_final=True, lower=x_lb, ref0=x_lb, upper=x_ub, ref=x_ub)
phase.set_state_options('BM_y', fix_initial=True, fix_final=True, lower=y_lb, ref0=y_lb, upper=y_ub, ref=y_ub)
phase.set_state_options('BM_omega', fix_initial=True, fix_final=True)
phase.set_state_options('BM_theta', fix_initial=True, fix_final=True, lower=-np.pi/2, ref0=-np.pi/2, upper=np.pi/2, ref=np.pi/2)

phase.set_control_options("PT_u1", lower=0, upper=1, opt=True, ref0=0.0, ref=1)
phase.set_control_options("PT_u2", lower=0, upper=1, opt=True, ref0=0.0, ref=1)

phase.add_boundary_constraint('PT.x2_dot', loc='final', shape=(1,), equals=0) # Shape may need to change to (nn,)
phase.add_boundary_constraint('PT.x3_dot', loc='final', shape=(1,), equals=0)
phase.add_boundary_constraint('BM.v_y_dot', loc='final', shape=(1,), equals=0)
phase.add_boundary_constraint('BM.omega_dot', loc='final', shape=(1,), equals=0)

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
prob.driver.add_recorder(recorder)
prob.driver.recording_options['includes']= ["thrust_ratio.*", "traj.phases.phase0.timeseries.*"]
prob.driver.recording_options['record_derivatives'] = False

prob.setup()

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

# Parameter Values
# set the battery mass to 0 initially
prob.set_val('traj.phase0.parameters:PT_theta16', 0)

prob.final_setup()

#%%
#
# Run the Optimization Problem for Various Masses
#
mass_vals = np.arange(0.0, 2.1, 0.1)
for (i,val) in enumerate(mass_vals):
    prob.set_val('traj.phase0.parameters:PT_theta16', val)
    print(f"Solving optimization for mass {val}")
    prob.run_driver(case_prefix=f'massval_{i}')
    final_time = prob.get_val('traj.phase0.t_duration').copy()
    print(f"Final time: {final_time}")
    prob.record(f'final_massval_{i}')
prob.cleanup()


#sim_out = traj.simulate(times_per_seg=50)
# Get the final value of the design variable

#%% Plots
cr = om.CaseReader('cases.sql')
prob_cases = cr.get_cases('problem')


plt_vars = ['mass.Mass__PlanarQuadrotor', 'thrust_ratio.TR', "traj.phase0.t_duration"]
labels = ["System Mass (kg)", "Thrust Ratio (N/kg)", "Minimum Time (s)"]
fig, axes = plt.subplots(len(plt_vars), 1, figsize=(4,6), dpi=300)
for (i, var) in enumerate(plt_vars):
    vals = [case[var] for case in prob_cases]  
    axes[i].plot(mass_vals, vals)
    axes[i].set_ylabel(labels[i])
    axes[i].set_ylim(bottom=0)
    if i == 1:
        axes[i].axhline(y = 1, color = 'r', linestyle = 'dashed', label = "red line")
axes[-1].set_xlabel("Mass (kg)")
fig.suptitle(r"\textbf{Battery Mass Sweep}")
plt.tight_layout()
plt.savefig("batt_mass_vs_time.png")
plt.show()



    
