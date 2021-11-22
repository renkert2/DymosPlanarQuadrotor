# -*- coding: utf-8 -*-
"""
Created on Sat Nov 20 20:19:34 2021

@author: renkert2
"""

import numpy as np
import openmdao.api as om
import matplotlib.pyplot as plt
import os
import sys

sys.path.append("C:/Users/renkert2/Documents/ARG_Research/DymosPlanarQuadrotor/PlanarPT")
os.chdir(os.path.dirname(__file__))
readers = [om.CaseReader(file) for file in ["BattSweep_4S_500.sql","BattSweep_4S_6000.sql"]]
cases = [reader.get_case('final') for reader in readers]
lgnd_labels = ["4S 500mAh", "4S 6000mAh"]

# Position Comparisons
fig, axs = plt.subplots(nrows=2, dpi=600)
subplot_labels = ["BM_x", "BM_y"]
subplot_vars =  ['traj.phases.phase0.timeseries.states:BM_x','traj.phases.phase0.timeseries.states:BM_y']
for i,ax in enumerate(axs):
    for j,case in enumerate(cases):
        x = case["traj.phases.phase0.timeseries.time"]
        data = case[subplot_vars[i]]
        ax.plot(x, data, label=lgnd_labels[j])
    ax.set_title(subplot_labels[i])
    ax.set_xlabel('time (s)')
    ax.legend()
plt.tight_layout()

# Input Comparisons
fig, axs = plt.subplots(nrows=2, dpi=600)
subplot_labels = ["PT_u1", "PT_u2"]
subplot_vars =  ['traj.phases.phase0.timeseries.controls:PT_u1','traj.phases.phase0.timeseries.controls:PT_u2']
for i,ax in enumerate(axs):
    for j,case in enumerate(cases):
        x = case["traj.phases.phase0.timeseries.time"]
        data = case[subplot_vars[i]]
        ax.plot(x, data, label=lgnd_labels[j])
    ax.set_title(subplot_labels[i])
    ax.set_xlabel('time (s)')
    ax.legend()
plt.tight_layout()
    
#%% Thrust Comparisons
fig, axs = plt.subplots(nrows=2, dpi=600)
subplot_labels = ["Thrust1", "Thrust2"]
subplot_vars =  ['traj.phases.phase0.timeseries.outputs:y12','traj.phases.phase0.timeseries.outputs:y14']
for i,ax in enumerate(axs):
    for j,case in enumerate(cases):
        x = case["traj.phases.phase0.timeseries.time"]
        data = case[subplot_vars[i]]
        ax.plot(x, data, label=lgnd_labels[j])
    ax.set_title(subplot_labels[i])
    ax.set_xlabel('time (s)')
    ax.legend()
plt.tight_layout()
    
#%% Voltage Comparisons
fig, ax = plt.subplots(nrows=1, dpi=600)
subplot_labels = "Voltage"
subplot_vars =  'traj.phases.phase0.timeseries.outputs:y4'
for j,case in enumerate(cases):
    x = case["traj.phases.phase0.timeseries.time"]
    data = case[subplot_vars]
    ax.plot(x, data, label=lgnd_labels[j])
ax.set_title(subplot_labels)
ax.set_xlabel('time (s)')
ax.legend()
plt.tight_layout()

#%% Series Resistance
fig, ax = plt.subplots(nrows=1, dpi=600)
subplot_labels = "Resistance"
subplot_vars =  'traj.phases.phase0.timeseries.parameters:PT_R_s__Battery'
for j,case in enumerate(cases):
    x = case["traj.phases.phase0.timeseries.time"]
    data = case[subplot_vars]
    print(lgnd_labels[j] + " Resistance: " + str(data[0]))
    ax.plot(x, data, label=lgnd_labels[j])
ax.set_title(subplot_labels)
ax.set_xlabel('time (s)')
ax.legend()
plt.tight_layout()