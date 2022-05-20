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
fig, axes = plt.subplots(1,2, figsize=[12,3])
fig.suptitle(r"\textbf{Battery Sweep}")

Q = []
final_times = []
for case in cases[0]:
    Q.append(case.get_val("params.Q__Battery"))
    final_times.append(case.get_val("traj.phase0.t_duration"))

axes[0].plot(Q, final_times)
axes[0].set_ylabel("Final Time (s)")
axes[0].set_xlabel("Battery Capacity $Q$ (mAh)")

axes[0].axvline(x=4000, ls='--', c='r', label="Nominal")

axes[0].legend()

N_s = []
final_times = []
for case in cases[1]:
    ns = case.get_val("params.N_s__Battery")
    if ns >= 3: # Hard check for feasibility
        N_s.append(ns)
        final_times.append(case.get_val("traj.phase0.t_duration"))

axes[1].plot(N_s, final_times)
axes[1].set_ylabel("Final Time (s)")
axes[1].set_xlabel("Series Cells $N_s$")

axes[1].axvline(x=4, ls='--', c='r', label="Nominal")

axes[1].legend()

#%%
import my_plt
import weekly_reports
import os
wr_dir = os.path.join(weekly_reports.WEEKLY_REPORTS, "Renkert_WeeklyReport_03232022")
my_plt.export(fig, fname="battery_sweep_condensed", directory=wr_dir)
