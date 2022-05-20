# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 17:03:38 2022

@author: renkert2
"""
import openmdao.api as om
import matplotlib.pyplot as plt
import SUPPORT_FUNCTIONS.plotting # Just to get the default formatting
import SUPPORT_FUNCTIONS.init as init
import Sweeps as sweep

init.init_output(__file__)

#%% Read Recorders
readers = [om.CaseReader(x) for x in ["D__Propeller_sweep_cases.sql", "P__Propeller_sweep_cases.sql"]]
cases = [r.get_cases("problem") for r in readers]

#%% D Sweep
d_cases = cases[0]
for case in d_cases:
    tr = case.get_val("thrust_ratio.TR")[0]
    if (tr < 1) or (tr > 10):
        d_cases.remove(case)

(fig, axes) = sweep.plot_sweeps(d_cases, "D__Propeller", ["traj.phase0.t_duration", "thrust_ratio.TR"])
fig.suptitle(r"\textbf{Propeller Diameter Sweep}")
axes[0].set_ylabel("Final Time (s)")
axes[1].set_ylabel("Thrust Ratio")
axes[-1].set_xlabel("Propeller Diameter $D$ (m)")
plt.savefig("D__Propeller_sweep.png")

#%% P Sweep
p_cases = cases[1]
for case in p_cases:
    tr = case.get_val("thrust_ratio.TR")[0]
    if (tr < 1) or (tr > 10):
        p_cases.remove(case)

(fig, axes) = sweep.plot_sweeps(p_cases, "P__Propeller", ["traj.phase0.t_duration", "thrust_ratio.TR"])
fig.suptitle(r"\textbf{Propeller Pitch Sweep}")
axes[0].set_ylabel("Final Time (s)")
axes[1].set_ylabel("Thrust Ratio")
axes[-1].set_xlabel("Propeller Pitch $P$ (m)")
plt.savefig("P__Propeller_sweep.png")


