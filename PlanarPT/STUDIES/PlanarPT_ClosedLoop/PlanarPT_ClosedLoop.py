# -*- coding: utf-8 -*-
"""
Created on Fri Mar 11 11:53:42 2022

@author: renkert2
"""
import SUPPORT_FUNCTIONS.init as init
import os
import dymos as dm
import openmdao.api as om
import time
import matplotlib.pyplot as plt
import logging
import DynamicModel as DM
import Param as P
import PlanarPT.PlanarPTModels as ppt
import PlanarPT.PlanarPT_Controller as pptc
import my_plt
logging.basicConfig(level=logging.INFO)

init.init_output(__file__)

#%%
nn = 50
tx = dm.GaussLobatto(num_segments=nn, solve_segments='forward', compressed=True)

# Phase
phase = ppt.PlanarPTDynamicPhase(transcription=tx, include_controller=True)
phase.init_vars(openmdao_path="PT")
pptc.ModifyPhase(phase, openmdao_path="CTRL", powertrain_path="PT")
     
phase.set_time_options(fix_initial=True, fix_duration=True, initial_val=0, duration_val=5)

phase.set_state_options("PT_x1", val=1, lower=0, upper=1, fix_initial=True, ref0 = 0, ref=1) # Fix Battery State of Charge Initial State to 1
phase.set_state_options("PT_x2", fix_initial=True, fix_final=False, lower=0, upper=5000, ref0=0.0, ref=5000) # Scaling ref=5000 has the largest impact on the solution
phase.set_state_options("PT_x3", fix_initial=True, fix_final=False, lower=0, upper=5000, ref0=0.0, ref=5000) # Scaling ref=5000 has the largest impact on the solution

phase.set_control_options("CTRL_omega_1_des", val=0, opt=False)
phase.set_control_options("CTRL_omega_2_des", val=0, opt=False)

phase.add_objective('time', loc='final')

# Trajectory
traj = ppt.PlanarPTDynamicTraj(phase)
traj.init_vars(openmdao_path = "PT" ,rename_vars=False)
pptc.ModifyTraj(traj, openmdao_path = "CTRL")

# Parameters
param_set = ppt.PlanarPTParams()
param_set.update(pptc.PlanarControllerParams())

param_group = P.ParamGroup(param_set)
# System
sys = P.ParamSystem(param_group)
sys.add_subsystem("traj", traj)

prob = om.Problem(model=sys)
prob.driver = om.ScipyOptimizeDriver()
#prob.driver.options["debug_print"] = ['desvars', 'nl_cons', 'ln_cons', 'objs', 'totals']
prob.driver.options["maxiter"] = 500
prob.driver.options["tol"] = 1e-9
prob.model.linear_solver = om.DirectSolver() # I'm not sure why we need this



prob.setup()
prob.final_setup()
#om.n2(prob)

#%%
# Set Initial Values
prob.set_val('traj.phase0.t_initial', 0.0)
prob.set_val('traj.phase0.t_duration', 5.0)

prob.set_val('traj.phase0.states:CTRL_e_omega_1_I',0)
prob.set_val('traj.phase0.states:CTRL_e_omega_2_I',0)


prob.set_val('traj.phase0.controls:CTRL_omega_1_des', phase.interp('CTRL_omega_1_des', ys=(0,0,2000,2000,200,200), xs=((0,1,1,5,5,10))))
prob.set_val('traj.phase0.controls:CTRL_omega_2_des', phase.interp('CTRL_omega_2_des', ys=(0,0,2000,2000,200,200), xs=((0,1,1,5,5,10))))

prob.set_val('traj.phase0.states:PT_x1', 1.0)
prob.set_val('traj.phase0.states:PT_x2', 0)
prob.set_val('traj.phase0.states:PT_x3', 0)

# Controller Tuning
param_set["k_p_omega"].val = 0.0007
param_set["k_i_omega"].val = 0.004
param_set["k_b_omega"].val = 2000


#
tic = time.perf_counter()
#prob.run_driver()
prob.run_model()
#sim_prob = traj.simulate()
toc = time.perf_counter()
run_time = toc-tic

#%% Plots

# Powertrain States
states = ["PT_x1", "PT_x2", "PT_x3"]
labels = ["$q$", r"$\omega_1$ (rad/s)", r"$\omega_2$ (rad/s)"]
fig, axes = plt.subplots(len(states), 1)
fig.suptitle(r"PowerTrain States", fontweight='bold')
for i, state in enumerate(states):
    sim = axes[i].plot(prob.get_val("traj.phases.phase0.timeseries.time"), prob.get_val(f'traj.phase0.timeseries.states:{state}'), '-')
    axes[i].set_ylabel(labels[i])
axes[-1].set_xlabel('time (s)')
plt.tight_layout()

#%%
states = ["CTRL_u_1", "CTRL_u_2"]
labels = ["$u_1$", "$u_2$"]
fig, axes = plt.subplots(len(states), 1)
fig.suptitle(r"PowerTrain Controls", fontweight='bold')
for i, ctrl in enumerate(states):
    sim = axes[i].plot(prob.get_val("traj.phases.phase0.timeseries.time"), prob.get_val(f'traj.phase0.timeseries.{ctrl}'), '-')
    axes[i].set_ylabel(labels[i])
axes[-1].set_xlabel('time (s)')
plt.tight_layout()

plt.show()

#%%
fig, axes = plt.subplots(1,1)

fig.suptitle(r"Speed Controller", fontweight='bold')
axes.plot(prob.get_val("traj.phases.phase0.timeseries.time"), prob.get_val(f'traj.phase0.timeseries.states:PT_x2'), '-')
axes.plot(prob.get_val("traj.phases.phase0.timeseries.time"), prob.get_val(f'traj.phase0.timeseries.controls:CTRL_omega_1_des'), '--')
axes.set_xlabel('time (s)')
axes.set_ylabel("$\omega_1$ (rad/s)")
axes.legend(["Rotor Speed", "Rotor Speed Reference"])
plt.tight_layout()

my_plt.export(fig, fname="speed_controller_step")

#%%
fig, axes = plt.subplots(1,1)

fig.suptitle(r"Speed Controller", fontweight='bold')
axes.plot(prob.get_val("traj.phases.phase0.timeseries.time"), prob.get_val(f'traj.phase0.timeseries.CTRL_u_1'), '-')
axes.axhline(1, ls="--")
axes.set_xlabel('time (s)')
axes.set_ylabel("$u_1$")
axes.legend(["Input", "Max Input"])
plt.tight_layout()

my_plt.export(fig, fname="speed_controller_input")