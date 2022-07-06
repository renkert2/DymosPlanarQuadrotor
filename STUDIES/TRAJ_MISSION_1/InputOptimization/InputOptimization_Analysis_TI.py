# -*- coding: utf-8 -*--
"""
Created on Wed Apr  6 15:10:11 2022

@author: renkert2
"""

import openmdao.api as om
import SUPPORT_FUNCTIONS.plotting as plotting
import matplotlib.pyplot as plt
import SUPPORT_FUNCTIONS.init as init
import os

init.init_output(__file__)

name = "input_opt_cases"
sim_name= name+"_sim"

reader = om.CaseReader(name+".sql")
cases = reader.get_cases("problem")

sim_reader = om.CaseReader(sim_name+".sql")
sim_cases = sim_reader.get_cases("problem")

#%% 
print(reader.list_cases())
print(sim_reader.list_cases())

#%% Trajectory Plots
graphics = plotting.timeseries_plots(sim=[sim_cases[1]], prob=[cases[-1]], phases=[f"phase{i}" for i in range(5)], title="Input Optimization", legend=None)

plt.show()