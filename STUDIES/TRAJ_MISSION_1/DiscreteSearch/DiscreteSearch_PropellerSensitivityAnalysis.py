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
iters_sorted = result.sorted_iterations
opt_config = result.opt_iter.config
opt_batt = opt_config["Battery"]
opt_motor = opt_config["PMSMMotor"]

iters_filtered = []
for i in iters_sorted:
    config = i.config
    batt_test = config.approx_contains(opt_batt)
    motor_test = config.approx_contains(opt_motor)
    if batt_test and motor_test:
        iters_filtered.append(i)

for i in iters_filtered:
    print(i.config["Propeller"].model, i.obj_val)
    
obj_vals = [i.obj_val[0] for i in iters_filtered]
plt.hist(obj_vals)
plt.xlabel("Obj. Value")
plt.ylabel("Count")