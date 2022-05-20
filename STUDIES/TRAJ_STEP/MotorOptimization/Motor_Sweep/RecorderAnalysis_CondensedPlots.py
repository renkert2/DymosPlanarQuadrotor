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
readers = [om.CaseReader(x) for x in ["kV__Motor_sweep_cases.sql", "Rm__Motor_sweep_cases.sql"]]
cases = [r.get_cases("problem") for r in readers]

#%% Q Sweep
fig, axes = plt.subplots(1,2, figsize=[12,3])
fig.suptitle(r"\textbf{Motor Sweep}")

kV = []
final_times = []
for case in cases[0]:
    kv = case.get_val("params.kV__Motor")
    if kv >= 500:
        kV.append(kv)
        final_times.append(case.get_val("traj.phase0.t_duration"))

axes[0].plot(kV, final_times)
axes[0].set_ylabel("Final Time (s)")
axes[0].set_xlabel("Motor Speed Constant $kV$ (RPM/V)")

axes[0].axvline(x=965, ls='--', c='r', label="Nominal")

axes[0].legend()

Rm = []
final_times = []
for case in cases[1]:
    rm = case.get_val("params.Rm__Motor")
    if rm >= 0.03: # Hard check for feasibility
        Rm.append(rm)
        final_times.append(case.get_val("traj.phase0.t_duration"))

axes[1].plot(Rm, final_times)
axes[1].set_ylabel("Final Time (s)")
axes[1].set_xlabel("Motor Resistance $Rm$ ($\\Omega$)")

axes[1].axvline(x=0.102, ls='--', c='r', label="Nominal")

axes[1].legend()

#%%
import my_plt
import weekly_reports
import os
wr_dir = os.path.join(weekly_reports.WEEKLY_REPORTS, "Renkert_WeeklyReport_03232022")
my_plt.export(fig, fname="motor_sweep_condensed", directory=wr_dir)
