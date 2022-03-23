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
readers = [om.CaseReader(x) for x in ["Q__Battery_sweep_cases.sql", "N_s__Battery_sweep_cases.sql"]]
cases = [r.get_cases("problem") for r in readers]

#%% Q Sweep

Q = []
final_times = []
thrust_ratio = []
r_p = []
for case in cases[0]:
    Q.append(case.get_val("params.Q__Battery"))
    final_times.append(case.get_val("traj.phase0.t_duration"))
    thrust_ratio.append(case.get_val("thrust_ratio.TR"))
    r_p.append(case.get_val("params.R_p__Battery"))

fig, axes = plt.subplots(3,1, figsize=[4,6])
fig.suptitle(r"\textbf{Battery Capacity Sweep}")

axes[0].plot(Q, final_times)
axes[0].set_ylabel("Final Time (s)")

axes[1].plot(Q, thrust_ratio)
axes[1].set_ylabel("Thrust Ratio")

axes[2].plot(Q, r_p)
axes[2].set_ylabel("Pack Resistance ($\\Omega$)")

axes[-1].set_xlabel("Battery Capacity $Q$ (mAh)")

plt.savefig("Q__Battery_sweep.png")

#%% N_s Sweep

N_s = []
final_times = []
thrust_ratio = []
r_p = []
for case in cases[1]:
    N_s.append(case.get_val("params.N_s__Battery"))
    final_times.append(case.get_val("traj.phase0.t_duration"))
    thrust_ratio.append(case.get_val("thrust_ratio.TR"))
    r_p.append(case.get_val("params.R_p__Battery"))

fig, axes = plt.subplots(3,1, figsize=[4,6])
fig.suptitle(r"\textbf{Battery Series Cells Sweep}")

axes[0].plot(N_s, final_times)
axes[0].set_ylabel("Final Time (s)")

axes[1].plot(N_s, thrust_ratio)
axes[1].set_ylabel("Thrust Ratio")

axes[2].plot(N_s, r_p)
axes[2].set_ylabel("Pack Resistance ($\\Omega$)")

axes[-1].set_xlabel("Series Cells $N_s$")

plt.savefig("N_s__Battery_sweep.png")