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

from ARG_Research_Python import my_plt
from ARG_Research_Python import weekly_reports

import PlanarSystem as PS

import logging
logging.basicConfig(level=logging.INFO)

init.init_output(__file__)
reader = search.SearchReader(output_dir = "search_output")

#%% Read Search Result
result = reader.result
ga_instance = result.ga_instance

ga_instance.plot_result()
ax = plt.gca()
ax.set_ylim(-3.5,-2)

wdir = weekly_reports.find_dir("05252022")[-1]
f = plt.gcf()
my_plt.export(f, fname="ga_fitness_vs_generation", directory=wdir)

#%%
ga_instance.plot_new_solution_rate()

#%%
best_fitness = max(ga_instance.best_solutions_fitness)
for i in result.iterations:
    if i.obj_val and abs(float(i.obj_val)) == abs(best_fitness):
        best_iter = i
        
        break
    
#%%
case_reader = reader.case_reader
case_reader.delta_table(init_case_name="base_case", final_case_name=result.opt_iter.case_name)

base_case = case_reader.get_case("base_case")
final_case = case_reader.get_case(result.opt_iter.case_name)

#%%
fig, ax = result.plot()
my_plt.export(fig, fname="discrete_search_result_05112022", directory=os.path.join(weekly_reports.WEEKLY_REPORTS, "Renkert_WeeklyReport_05182022"))

# #%% Function Evaluations at Optimal Config
# opt_iters = result.iterations[:57]
# total_fevals = sum([x.func_evals for x in opt_iters])
# print(f"Func Evals to find Optimal Configuration: {total_fevals}")

#%% Reattach component searchers, need to fix
p = PS.PlanarSystemParams()
s = PS.PlanarSystemSurrogates(p)
s.setup()

target_path = os.path.join(init.HOME_PATH, "STUDIES", "SystemOptimization", "Output", "pv_opt.pickle")
with open(target_path, 'rb') as f:
    target = pickle.load(f)

comp_searchers = {}
for (k,v) in s.surrogates.items():
    comp_searchers[k] = search.ComponentSearcher(v)
    comp_searchers[k].set_target(target)

result.config_searcher.component_searchers = comp_searchers

#%%
figs = result.plotDesignSpace()
names = ["batt_design_space_search", "motor_design_space_search", "prop_design_space_search"]
from ARG_Research_Python import my_plt
for (f,n) in zip(figs,names):
    my_plt.export(f, fname=n, directory=os.path.join(weekly_reports.WEEKLY_REPORTS, "Renkert_WeeklyReport_05182022"))

#%% Plot Design Space of First Iteration
figs = result.config_searcher.plotDesignSpace(result.iterations[0].config, config_name="Closest Config.")

#%% Plot Heatmaps of Mean Obj. Value
figs = result.plotCompHeatmat(stat_func=np.mean, stat_func_label="Mean Obj. Value")
names = ["batt_design_space_meanval", "motor_design_space_meanval", "prop_design_space_meanval"]
from ARG_Research_Python import my_plt
for (f,n) in zip(figs,names):
    my_plt.export(f, fname=n, directory=os.path.join(weekly_reports.WEEKLY_REPORTS, "Renkert_WeeklyReport_05182022"))

#%% Plot Heatmaps ob Min Obj. Value
figs = result.plotCompHeatmat(stat_func=np.min, stat_func_label="Min Obj. Value")
names = ["batt_design_space_minval", "motor_design_space_minval", "prop_design_space_minval"]
from ARG_Research_Python import my_plt
for (f,n) in zip(figs,names):
    my_plt.export(f, fname=n, directory=os.path.join(weekly_reports.WEEKLY_REPORTS, "Renkert_WeeklyReport_05182022"))
    
#%%
result.showTopComps()