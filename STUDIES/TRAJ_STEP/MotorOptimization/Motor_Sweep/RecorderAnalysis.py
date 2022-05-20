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

cases = []
for r in readers:
    case_list=r.get_cases("problem")
    good_cases = []
    for case in case_list:
        tr = case.get_val("thrust_ratio.TR")[0]
        if (tr > 1) and (tr < 10):
            good_cases.append(case)
    cases.append(good_cases)

#%% kV Sweep
kV = []
final_times = []
thrust_ratio = []
for case in cases[0]:
    kV.append(case.get_val("params.kV__Motor"))
    final_times.append(case.get_val("traj.phase0.t_duration"))
    thrust_ratio.append(case.get_val("thrust_ratio.TR"))

fig, axes = plt.subplots(2,1, figsize=[6,4])
fig.suptitle(r"\textbf{Motor Speed Constant Sweep}")

axes[0].plot(kV, final_times)
axes[0].set_ylabel("Final Time (s)")

axes[1].plot(kV, thrust_ratio)
axes[1].set_ylabel("Thrust Ratio")

axes[-1].set_xlabel("Motor Speed Constant $kV$ (RPM/V)")

plt.savefig("kV__Motor_sweep.png")

#%% N_s Sweep

Rm = []
final_times = []
thrust_ratio = []
for case in cases[1]:
    Rm.append(case.get_val("params.Rm__Motor"))
    final_times.append(case.get_val("traj.phase0.t_duration"))
    thrust_ratio.append(case.get_val("thrust_ratio.TR"))

fig, axes = plt.subplots(2,1, figsize=[6,4])
fig.suptitle(r"\textbf{Motor Resistance Sweep}")

axes[0].plot(Rm, final_times)
axes[0].set_ylabel("Final Time (s)")

axes[1].plot(Rm, thrust_ratio)
axes[1].set_ylabel("Thrust Ratio")

axes[-1].set_xlabel("Motor Resistance $Rm$ ($\\Omega$)")

plt.savefig("Rm__Motor_sweep.png")