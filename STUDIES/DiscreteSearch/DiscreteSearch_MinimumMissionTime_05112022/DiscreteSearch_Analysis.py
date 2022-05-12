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

import PlanarSystem as PS


init.init_output(__file__)
reader = search.SearchReader(output_dir = "search_output")

#%% Read problem cases
case_reader = reader.case_reader
prob_cases = reader.problem_cases

#%% Read Search Result
result = reader.result
print(result)

#%%
fig, ax = result.plot()
# import my_plt
# my_plt.export(fig, fname="discrete_search_result_05112022")

#%% Function Evaluations at Optimal Config
opt_iters = result.iterations[:57]
total_fevals = sum([x.func_evals for x in opt_iters])
print(f"Func Evals to find Optimal Configuration: {total_fevals}")

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
# names = ["batt_design_space_search", "motor_design_space_search", "prop_design_space_search"]
# import my_plt
# for (f,n) in zip(figs,names):
#     my_plt.export(f, fname=n)

#%% Plot Design Space of First Iteration
figs = result.config_searcher.plotDesignSpace(result.iterations[0].config, config_name="Closest Config.")