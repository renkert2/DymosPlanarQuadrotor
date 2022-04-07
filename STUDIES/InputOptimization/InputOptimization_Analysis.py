# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 15:10:11 2022

@author: renkert2
"""

import openmdao.api as om
import SUPPORT_FUNCTIONS.plotting as plotting
import my_plt
import matplotlib.pyplot as plt
import SUPPORT_FUNCTIONS.init as init
import os

init.init_output(__file__)

name = "input_opt_cases"
sim_name= name+"_sim"

reader = om.CaseReader(name+".sql")
cases = reader.get_cases("problem")

sim_reader = om.CaseReader(sim_name+".sql")
sim_cases = sim_reader.get_cases("problem")

#%% 
print(reader.list_cases())
print(sim_reader.list_cases())

#%% Trajectory Comparisons
(fig, axes) = plotting.subplots(cases, sim_cases, path='traj.phase0.timeseries', save=False, 
                                vars=[f"states:{x}" for x in  ['BM_x', 'BM_y', 'BM_theta']] + [f"controls:{x}" for x in  ['PT_u1', 'PT_u2']],
                                labels=['$x$', '$y$', r'$\theta$', "$u_1$", "$u_2$"], 
                                title="Planar Quadrotor Input Optimization", 
                                legend=["Initial", "Final"])

#%% Driver Output
driver_cases = reader.get_cases("driver")
last_case = driver_cases[-1]

