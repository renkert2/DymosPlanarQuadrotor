# -*- coding: utf-8 -*-
"""
Created on Mon May  2 15:00:51 2022

@author: renkert2
"""
import os
import openmdao.api as om
import pickle
import logging
logging.basicConfig(level=logging.INFO)

import SUPPORT_FUNCTIONS.init as init
import PlanarSystem as PS
import OPTIM.Search as Search
import Trajectories as T
import Problems as P
import OPTIM.Count as Count
import Constraints as C

import OPTIM.Search as search

init.init_output(__file__)

#%% Setup Search Recorder
rec = Search.SearchRecorder(append_mode = True)
# Creates recorder for problem internally

#%% Setup Problem
traj = T.Mission_1()
cons = C.ConstraintSet() # Create an empty constraint set
#TODO: cons.add(C.BatteryCurrent()) for multiple phases
cons.add(C.InverterCurrent())
model = PS.PlanarSystemSearchModel(traj, cons=cons)
prob = P.Problem(model=model, traj=traj, planar_recorder=None, record_driver=False)
prob.driver.options["maxiter"] = 750 # More complicated trajectory hits default iteration limit, need to increase
rec.add_prob(prob)

prob.setup()
prob.init_vals()

#%% Setup Config Searcher
p = model._params
s = PS.PlanarSystemSurrogates(p)
s.setup()

target_path = os.path.join(os.path.dirname(__file__), "..", "SystemOptimization", "Output", "pv_opt.pickle")
with open(target_path, 'rb') as f:
    target = pickle.load(f)

comp_searchers = {}
for (k,v) in s.surrogates.items():
    comp_searchers[k] = Search.ComponentSearcher(v)
    comp_searchers[k].set_target(target)

config_searcher = Search.ConfigurationSearcher(comp_searchers)
config_searcher.run()

#%% Setup Searcher
input_opt_path = os.path.join(os.path.dirname(__file__), "..", "InputOptimization", "Output")
reader = om.CaseReader(os.path.join(input_opt_path, "input_opt_cases.sql"))
base_case = reader.get_case("input_opt_final")
counter = Count.Counter()

searcher = Search.Searcher(config_searcher=config_searcher, prob=prob, params=model._params, search_recorder=rec, base_case=base_case, counter=counter)

#%% Test 1: Searching up to 100 Configurations
recovery_reader = search.SearchReader(output_dir = "search_output_recover")
search_result = searcher.restore_result(recovery_reader)


#%%
prob.cleanup_all()
