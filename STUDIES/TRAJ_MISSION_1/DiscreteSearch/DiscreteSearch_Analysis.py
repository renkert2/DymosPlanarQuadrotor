# -*- coding: utf-8 -*-
"""
Created on Thu May  5 08:43:02 2022

@author: renkert2
"""

import os
import pickle
import openmdao.api as om
import SUPPORT_FUNCTIONS.init as init
import SUPPORT_FUNCTIONS.pickling as my_pickle
import OPTIM.Search as search
import matplotlib.pyplot as plt
import numpy as np

import PlanarSystem as PS
import Recorders as R

import logging
logging.basicConfig(level=logging.INFO)

init.init_output(__file__, dirname="Output_20")
reader = search.SearchReader(output_dir = "search_output")

#%% Read Search Result
result = reader.result

print(result)

#%% Reattach component searchers, need to fix
p = PS.PlanarSystemParams()
s = PS.PlanarSystemSurrogates(p)
s.setup()

target_path = os.path.join(init.HOME_PATH, "STUDIES", "TRAJ_MISSION_1", "SystemOptimization", "Output_20", "pv_opt.pickle")
with open(target_path, 'rb') as f:
    target = my_pickle.renamed_load(f)

comp_searchers = {}
for (k,v) in s.surrogates.items():
    comp_searchers[k] = search.ComponentSearcher(v)
    comp_searchers[k].set_target(target)

result.config_searcher.component_searchers = comp_searchers


#%%
case_reader_0 = reader.case_reader
case_reader_1 = R.Reader(os.path.join(reader.output_dir, "search_cases_1.sql"))

base_case = case_reader_0.get_case("base_case")
final_case = case_reader_1.get_case(result.opt_iter.case_name)

R.delta_table(base_case, final_case)

#%%
pv = result.opt_iter.config.data
for param in p:
    pv_ = param.get_compatible(pv)
    if pv_:
        init_val = param.val
        final_val = pv_.val
        rel_change = (final_val - init_val)/init_val
        print(f"{param.strID}: Initial={init_val}, Final={final_val}, change={rel_change}")

#%%
fig, ax = result.plot()
from ARG_Research_Python import my_plt
from ARG_Research_Python import weekly_reports
#my_plt.export(fig, fname="discrete_search_result", directory=os.path.join(weekly_reports.WEEKLY_REPORTS, "Renkert_WeeklyReport_06292022"))

#%% Function Evaluations at Optimal Config
opt_iters = result.iterations[:70]
total_fevals = sum([x.func_evals for x in opt_iters])
print(f"Func Evals to find Optimal Configuration: {total_fevals}")



#%%
figs = result.plotDesignSpace()
names = ["batt_design_space_search", "motor_design_space_search", "prop_design_space_search"]
from ARG_Research_Python import my_plt
for (f,n) in zip(figs,names):
    my_plt.export(f, fname=n, directory=os.path.join(weekly_reports.WEEKLY_REPORTS, "Renkert_WeeklyReport_06292022"))

#%% Plot Design Space of First Iteration
figs = result.config_searcher.plotDesignSpace(result.iterations[0].config, config_name="Closest Config.")

#%% Plot Heatmaps of Mean Obj. Value
figs = result.plotCompHeatmat(stat_func=np.mean, stat_func_label="Mean Obj. Value")
names = ["batt_design_space_meanval", "motor_design_space_meanval", "prop_design_space_meanval"]
from ARG_Research_Python import my_plt
for (f,n) in zip(figs,names):
    my_plt.export(f, fname=n, directory=os.path.join(weekly_reports.WEEKLY_REPORTS, "Renkert_WeeklyReport_06292022"))

#%% Plot Heatmaps ob Min Obj. Value
figs = result.plotCompHeatmat(stat_func=np.min, stat_func_label="Min Obj. Value")
names = ["batt_design_space_minval", "motor_design_space_minval", "prop_design_space_minval"]
from ARG_Research_Python import my_plt
for (f,n) in zip(figs,names):
    my_plt.export(f, fname=n, directory=os.path.join(weekly_reports.WEEKLY_REPORTS, "Renkert_WeeklyReport_06292022"))
    
#%%
result.showTopComps()

#%%
import SUPPORT_FUNCTIONS.plotting as plotting
graphics = plotting.timeseries_plots(sim=[final_case], phases=[f"phase{i}" for i in range(5)], title="Discrete Search Result Optimization", legend=None, show_plts=[1])

#%% Evaluate Failed Case
failed_case = case_reader.get_case('iteration_98')
graphics = plotting.timeseries_plots(sim=[failed_case], phases=[f"phase{i}" for i in range(5)], title="Discrete Search Result Optimization", legend=None)
