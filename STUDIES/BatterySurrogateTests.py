# -*- coding: utf-8 -*-
"""
Created on Sat Nov 20 17:23:20 2021

@author: renkert2
"""

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
phase = ps.PlanarSystemDynamicPhase(tx)

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

planar_model, traj = ps.makePlanarSystemModel(phase)
#planar_model.add_design_var('N_s__Battery', lower=1, upper=6, ref0=1, ref=6)
planar_model.add_design_var('Q__Battery', lower=500, upper=6000, ref0=500, ref=6000)

prob = om.Problem(model=planar_model)
prob.driver = om.ScipyOptimizeDriver()
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

# Initial Parameter Values
prob.set_val('N_s__Battery', val=4)
prob.set_val('Q__Battery', val=4000)

#%%
prob.set_val('Q__Battery', val=500)
prob.run_model()
print(prob.get_val("Mass"))

prob.set_val('Q__Battery', val=6000)
prob.run_model()
print(prob.get_val("Mass"))

prob.set_val('Q__Battery', val=4000)

#%%
prob.set_val('N_s__Battery', val=1)
prob.run_model()
print(prob.get_val("Mass"))

prob.set_val('N_s__Battery', val=6)
prob.run_model()
print(prob.get_val("Mass"))

prob.set_val('N_s__Battery', val=4)
