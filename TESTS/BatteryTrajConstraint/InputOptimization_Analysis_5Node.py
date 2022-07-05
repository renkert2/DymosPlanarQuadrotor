# -*- coding: utf-8 -*--
"""
Created on Wed Apr  6 15:10:11 2022

@author: renkert2
"""

import openmdao.api as om
import SUPPORT_FUNCTIONS.plotting as plotting
import my_plt
import matplotlib.pyplot as plt
import SUPPORT_FUNCTIONS.init as init
import os

init.init_output(__file__)

tx_10_dir = os.path.join(os.path.dirname(__file__), "Output_5NodeTx/")
name = "input_opt_cases"
sim_name= name+"_sim"

reader = om.CaseReader(os.path.join(tx_10_dir, name+".sql"))
cases = reader.get_cases("problem")

sim_reader = om.CaseReader(os.path.join(tx_10_dir, sim_name+".sql"))
sim_cases = sim_reader.get_cases("problem")

#%% 
print(reader.list_cases())
print(sim_reader.list_cases())

#%% Trajectory Plots
#graphics = plotting.timeseries_plots(sim=[sim_cases[1]], phases=[f"phase{i}" for i in range(5)], title="Input Optimization", legend=None)
#graphics = plotting.timeseries_plots(prob=[cases[0], cases[-1]], phases=[f"phase{i}" for i in range(4)], title="Input Optimization", legend=None)

# Plot Powertrain States
graphics = plotting.timeseries_plots(prob=[cases[-1]], sim=[sim_cases[1]], phases=[f"phase{i}" for i in range(5)], title="Input Optimization, 5 Nodes", legend=None)

#%%
import weekly_reports
wdir = weekly_reports.find_dir("07062022")[-1]
figs = [x[0] for x in graphics]
fnames = [f"5nodes_mission1_{x}" for x in ["body_states", "powertrain_states", "inverter_currents", "inverter_inputs"]]

for (f,fname) in zip(figs, fnames):
    my_plt.export(f, fname=fname, directory=wdir)
    

#%% Driver Output
driver_cases = reader.get_cases("driver")
last_case = driver_cases[-1]

