# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 08:36:58 2021

@author: renkert2
"""

import os
import dymos as dm
import openmdao.api as om
import numpy as np

res_path = os.getenv('ARG_RESEARCH')
os.chdir(os.path.join(res_path, 'DymosPlanarQuadrotor'))
import PlanarSystem as ps
import SUPPORT_FUNCTIONS.plotting as my_plt # Just to get the default formatting
import SUPPORT_FUNCTIONS.init as init

init.init_study(__file__)
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


nn = 20
tx = dm.GaussLobatto(num_segments=nn)
phase = ps.PlanarSystemDynamicPhase(transcription=tx)
phase.init_vars()


# Set up States and Inputs as Optimization Variables
phase.set_time_options(fix_initial=True, fix_duration=True, initial_val=0, duration_val=10, duration_ref0=0, duration_ref=10)

phase.set_state_options("PT_x1", val=1, lower=0, upper=1, fix_initial=True, ref0 = 0, ref=1) # Fix Battery State of Charge Initial State to 1
phase.set_state_options("PT_x2", fix_initial=True, lower=0, upper=10000, ref0=0.0, ref=10000) # Scaling ref=5000 has the largest impact on the solution
phase.set_state_options("PT_x3", fix_initial=True, lower=0, upper=10000, ref0=0.0, ref=10000) # Scaling ref=5000 has the largest impact on the solution
phase.set_state_options('BM_v_x', fix_initial=False, fix_final=True)
phase.set_state_options('BM_v_y', fix_initial=False, fix_final=True)
phase.set_state_options('BM_x', fix_initial=True, fix_final=True)
phase.set_state_options('BM_y', fix_initial=True, fix_final=True)
phase.set_state_options('BM_omega', fix_initial=True, fix_final=True)
phase.set_state_options('BM_theta', fix_initial=True, fix_final=True, lower=-np.pi/2, ref0=-np.pi/2, upper=np.pi/2, ref=np.pi/2)

phase.set_control_options("PT_u1", lower=0, upper=1, opt=True, ref0=0.0, ref=1)
phase.set_control_options("PT_u2", lower=0, upper=1, opt=True, ref0=0.0, ref=1)

phase.add_boundary_constraint('PT.x2_dot', loc='final', shape=(1,), equals=0) # Shape may need to change to (nn,)
phase.add_boundary_constraint('PT.x3_dot', loc='final', shape=(1,), equals=0)
phase.add_boundary_constraint('BM.v_y_dot', loc='final', shape=(1,), equals=0)
phase.add_boundary_constraint('BM.omega_dot', loc='final', shape=(1,), equals=0)

traj = dm.Trajectory()
traj.add_phase('phase0', phase)
meta = phase.Metadata

planar_model=ps.PlanarSystemModel(traj, meta, IncludeSurrogates=[], IncludeStaticModel=True)

# Add Battery Mass as a design Variable
planar_model.add_design_var('traj.phase0.parameters:PT_theta16', lower=0, upper=2, ref0=0, ref=2)

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

planar_model.add_objective('thrust_ratio.TR', scaler=1)

prob.setup()


# Set Initial Values
prob.set_val('traj.phase0.t_initial', 0.0)

prob.set_val('traj.phase0.controls:PT_u1', 1)
prob.set_val('traj.phase0.controls:PT_u2', 1)

prob.set_val('traj.phase0.states:PT_x1', 1.0)
prob.set_val('traj.phase0.states:PT_x2', phase.interp('PT_x2', ys=(0,1000)))
prob.set_val('traj.phase0.states:PT_x3', phase.interp('PT_x3', ys=(0,1000)))
prob.set_val('traj.phase0.states:BM_v_x', phase.interp('BM_v_x', ys=[0, 0]))
prob.set_val('traj.phase0.states:BM_v_y', phase.interp('BM_v_y', ys=[0, 0]))
prob.set_val('traj.phase0.states:BM_x', phase.interp('BM_x', ys=[0, 0]))
prob.set_val('traj.phase0.states:BM_y', phase.interp('BM_y', ys=[0, 0]))
prob.set_val('traj.phase0.states:BM_omega', phase.interp('BM_omega', ys=[0, 0]))
prob.set_val('traj.phase0.states:BM_theta', phase.interp('BM_theta', ys=[0, 0]))

# Parameter Values
# set the battery mass to 0 initially
prob.set_val('traj.phase0.parameters:PT_theta16', 0)

#%% Minimize Time

prob.run_driver()
prob.record('final')
prob.cleanup()
sims = prob.model.traj.simulate(times_per_seg=50)

#%%
tr = prob.get_val('thrust_ratio.TR')
my_plt.subplots(sims, prob, path='traj.phase0.timeseries',
             vars=[f"states:{x}" for x in  ['BM_x', 'BM_y', 'BM_theta']] + [f"controls:{x}" for x in  ['PT_u1', 'PT_u2']],
             labels=['$x$', '$y$', r'$\theta$', "$u_1$", "$u_2$"], 
             title=f"Thrust Ratio Minimization: $TR = {tr}$", save=True)






    
