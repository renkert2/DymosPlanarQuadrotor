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
readers = [om.CaseReader(x) for x in ["D__Propeller_sweep_cases.sql", "P__Propeller_sweep_cases.sql"]]
cases = [r.get_cases("problem") for r in readers]

#%% Q Sweep
fig, axes = plt.subplots(1,2, figsize=[12,3])
fig.suptitle(r"\textbf{Propeller Sweep}")

D = []
final_times = []
for case in cases[0]:
    d = case.get_val("params.D__Propeller")
    if True:
        D.append(d)
        final_times.append(case.get_val("traj.phase0.t_duration"))

axes[0].plot(D, final_times)
axes[0].set_ylabel("Final Time (s)")
axes[0].set_xlabel("Propeller Diameter $D$ (m)")
axes[0].axvline(x=0.2286, ls='--', c='r', label="Nominal")
axes[0].legend()

P = []
final_times = []
for case in cases[1]:
    p = case.get_val("params.P__Propeller")
    if True: # Hard check for feasibility
        P.append(p)
        final_times.append(case.get_val("traj.phase0.t_duration"))

axes[1].plot(P, final_times)
axes[1].set_ylabel("Final Time (s)")
axes[1].set_xlabel("Propeller Pitch $P$ (m)")
axes[1].axvline(x=0.1143, ls='--', c='r', label="Nominal")
axes[1].legend()

#%%
import my_plt
import weekly_reports
import os
wr_dir = os.path.join(weekly_reports.WEEKLY_REPORTS, "Renkert_WeeklyReport_03232022")
my_plt.export(fig, fname="prop_sweep_condensed", directory=wr_dir)
