# -*- coding: utf-8 -*-
"""
Created on Thu May  5 08:43:02 2022

@author: renkert2
"""

import os
import pickle
import openmdao.api as om
import SUPPORT_FUNCTIONS.init as init
import OPTIM.Search as search
import matplotlib.pyplot as plt
import numpy as np

import PlanarSystem as PS

import logging
logging.basicConfig(level=logging.INFO)

init.init_output(__file__)
reader = search.SearchReader(output_dir = "search_output")

#%% Read Search Result
result = reader.result

print(result)

#%% Reattach component searchers, need to fix
p = PS.PlanarSystemParams()
s = PS.PlanarSystemSurrogates(p)
s.setup()

target_path = os.path.join(init.HOME_PATH, "STUDIES", "TRAJ_MISSION_1", "SystemOptimization", "Output", "pv_opt.pickle")
with open(target_path, 'rb') as f:
    target = pickle.load(f)

comp_searchers = {}
for (k,v) in s.surrogates.items():
    comp_searchers[k] = search.ComponentSearcher(v)
    comp_searchers[k].set_target(target)

result.config_searcher.component_searchers = comp_searchers


#%%
case_reader = reader.case_reader
case_reader.delta_table(init_case_name="base_case", final_case_name=result.opt_iter.case_name)

base_case = case_reader.get_case("base_case")
final_case = case_reader.get_case(result.opt_iter.case_name)

#%%
fig, ax = result.plot()
import my_plt
import weekly_reports
#my_plt.export(fig, fname="discrete_search_result", directory=os.path.join(weekly_reports.WEEKLY_REPORTS, "Renkert_WeeklyReport_06292022"))

#%% Function Evaluations at Optimal Config
opt_iters = result.iterations[:70]
total_fevals = sum([x.func_evals for x in opt_iters])
print(f"Func Evals to find Optimal Configuration: {total_fevals}")



#%%
figs = result.plotDesignSpace()
names = ["batt_design_space_search", "motor_design_space_search", "prop_design_space_search"]
import my_plt
for (f,n) in zip(figs,names):
    my_plt.export(f, fname=n, directory=os.path.join(weekly_reports.WEEKLY_REPORTS, "Renkert_WeeklyReport_06292022"))

#%% Plot Design Space of First Iteration
figs = result.config_searcher.plotDesignSpace(result.iterations[0].config, config_name="Closest Config.")

#%% Plot Heatmaps of Mean Obj. Value
figs = result.plotCompHeatmat(stat_func=np.mean, stat_func_label="Mean Obj. Value")
names = ["batt_design_space_meanval", "motor_design_space_meanval", "prop_design_space_meanval"]
import my_plt
for (f,n) in zip(figs,names):
    my_plt.export(f, fname=n, directory=os.path.join(weekly_reports.WEEKLY_REPORTS, "Renkert_WeeklyReport_06292022"))

#%% Plot Heatmaps ob Min Obj. Value
figs = result.plotCompHeatmat(stat_func=np.min, stat_func_label="Min Obj. Value")
names = ["batt_design_space_minval", "motor_design_space_minval", "prop_design_space_minval"]
import my_plt
for (f,n) in zip(figs,names):
    my_plt.export(f, fname=n, directory=os.path.join(weekly_reports.WEEKLY_REPORTS, "Renkert_WeeklyReport_06292022"))
    
#%%
result.showTopComps()

#%%
import SUPPORT_FUNCTIONS.plotting as plotting
graphics = plotting.timeseries_plots(sim=[final_case], phases=[f"phase{i}" for i in range(5)], title="Discrete Search Result Optimization", legend=None, show_plts=[1])