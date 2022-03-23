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

mass = []
final_times = []
thrust_ratio = []
for case in cases:
    mass.append(case.get_val("params.Mass__Frame"))
    final_times.append(case.get_val("traj.phase0.t_duration"))
    thrust_ratio.append(case.get_val("thrust_ratio.TR"))
#%% Plots

fig, axes = plt.subplots(2,1)
fig.suptitle(r"\textbf{Frame Mass Sweep}")

axes[0].plot(mass, final_times)
axes[0].set_ylabel("Final Time (s)")

axes[1].plot(mass, thrust_ratio)
axes[1].set_ylabel("Thrust Ratio")
axes[-1].set_xlabel("Frame Mass (kg)")

plt.savefig("frame_mass_sweep.png")