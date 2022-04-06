# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 18:13:54 2022

@author: renkert2
"""
import openmdao.api as om
import SUPPORT_FUNCTIONS.plotting as plotting
import my_plt
import matplotlib.pyplot as plt
import SUPPORT_FUNCTIONS.init as init
import os

init.init_output(__file__)

names = ["nocon_cases", "battcon_cases", "invcon_cases"]
sim_names= [n+"_sim" for n in names]


readers = [om.CaseReader(x+".sql") for x in names]
cases = [r.get_cases("problem")[0] for r in readers]

sim_readers = [om.CaseReader(x+".sql") for x in sim_names]
sim_cases = [r.get_cases("problem")[0] for r in readers]


#%% Print

(fig, axes) = plotting.subplots(None, sim_cases, path='traj.phase0.timeseries', save=False, 
                              vars=["outputs:PT_a2", "outputs:PT_a3", "outputs:PT_a5"], 
                              labels=["Battery Current (A)", "Inverter 1 Current (A)", "Inverter 2 Current (A)"], 
                              title="Current Constraints", 
                              legend=["None", "Battery Current", "Inverter Current"])

axes[0].axhline(y=42.0, linestyle="--", color='r', label="Constraint Value")
axes[0].legend()

axes[1].axhline(y=22.0, linestyle="--", color='r')

plt.show()

#%% Export
my_plt.export(fig, fname = "current_constraint_plots", title = None, directory = os.getcwd())
