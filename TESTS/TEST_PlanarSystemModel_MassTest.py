# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 07:30:25 2021

@author: renkert2
"""
import os
import openmdao.api as om
os.chdir(os.path.join(os.path.dirname(__file__), '..'))
import PlanarSystem as ps
import dymos as dm
import openmdao.api as om
import matplotlib.pyplot as plt
import time

#%%
nn = 20
tx = dm.Radau(num_segments=nn, compressed=False)
phase = ps.PlanarSystemDynamicPhase(tx)
planar_model, traj = ps.makePlanarSystemModel(phase)

planar_model.add_design_var('kV__Motor', lower=1500, upper=2000, ref0=105, ref=2550) # Initially 105-2550
planar_model.add_design_var('Rm__Motor', lower=0.1, upper=0.14, ref0=0.013, ref=0.171) # Initially 0.013-0.171

#%%
prob = om.Problem(model=planar_model)
prob.setup()

prob.set_val('traj.phase0.t_initial', 0.0)
prob.set_val('traj.phase0.t_duration', 50)

prob.set_val('traj.phase0.controls:PT_u1', 1)
prob.set_val('traj.phase0.controls:PT_u2', 1)

prob.run_model()

prob.set_val('kV__Motor', val=965)
prob.set_val('Rm__Motor', val=0.102)
prob.run_model()

print(prob.get_val("Mass"))

prob.set_val('kV__Motor', val=105)
prob.set_val('Rm__Motor', val=0.013)

prob.run_model()
mass = prob.get_val("Mass")
sim_out = traj.simulate(times_per_seg=50)

print(sim_out.get_val('traj.phase0.timeseries.states:PT_x2')[-1])
print(sim_out.get_val('traj.phase0.timeseries.outputs:y12')[-1])

total_thrust = sim_out.get_val('traj.phase0.timeseries.outputs:y12')[-1]
thrust_ratio = total_thrust/mass
print(thrust_ratio)

