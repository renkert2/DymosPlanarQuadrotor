# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 17:03:38 2022

@author: renkert2
"""
import openmdao.api as om
import matplotlib.pyplot as plt
import SUPPORT_FUNCTIONS.plotting # Just to get the default formatting
import SUPPORT_FUNCTIONS.init as init

init.init_output(__file__)

#%% Read Recorders
case_reader = om.CaseReader('cases.sql')
cases = case_reader.get_cases("problem")

# mass = []
# final_times = []
# thrust_ratio = []
# for case in cases:
#     mass.append(case.get_)
#%% Plots
# plt.subplots(sim_out, prob, path='traj.phase0.timeseries',
#              vars=[f"states:{x}" for x in  ['BM_x', 'BM_y', 'BM_theta']] + [f"controls:{x}" for x in  ['PT_u1', 'PT_u2']],
#              labels=['$x$', '$y$', r'$\theta$', "$u_1$", "$u_2$"], 
#              title="Planar Quadrotor Input Optimization", save=True)

# plt.plot(mass_vals, time_vals)
# plt.title("Frame Mass vs. Optimal Time")
# plt.xlabel("Mass (kg)")
# plt.ylabel("Time (s)")
# #plt.savefig("frame_mass_vs_time.png")