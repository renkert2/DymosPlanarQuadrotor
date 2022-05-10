# -*- coding: utf-8 -*-
"""
Created on Mon May  2 15:00:51 2022

@author: renkert2
"""
import os
import openmdao.api as om
import pickle
import logging
import random
logging.basicConfig(level=logging.INFO)

import SUPPORT_FUNCTIONS.init as init
import PlanarSystem as PS
import OPTIM.Search as Search
import Trajectories as T
import Problems as P
import OPTIM.Count as Count

init.init_output(__file__)

#%% Setup Search Recorder
rec = Search.SearchRecorder()
# Creates recorder for problem internally

#%% Setup Problem
traj = T.Step()

model = PS.PlanarSystemSearchModel(traj)
prob = P.Problem(model=model, traj=traj, planar_recorder=None, record_driver=False)
rec.add_prob(prob)

prob.setup()
prob.init_vals()

#%% Setup Config Searcher
p = model._params
s = PS.PlanarSystemSurrogates(p)
s.setup()

target_path = os.path.join(init.HOME_PATH, "STUDIES", "SystemOptimization", "Output", "pv_opt.pickle")
with open(target_path, 'rb') as f:
    target = pickle.load(f)

comp_searchers = {}
for (k,v) in s.surrogates.items():
    comp_searchers[k] = Search.ComponentSearcher(v)
    comp_searchers[k].set_target(target)

config_searcher = Search.ConfigurationSearcher(comp_searchers)
config_searcher.run()

#%% Setup Searcher
reader = om.CaseReader(os.path.join(init.INPUT_OPT_PATH, "input_opt_cases.sql"))
base_case = reader.get_case("input_opt_final")
counter = Count.Counter()

searcher = Search.Searcher(config_searcher=config_searcher, prob=prob, params=model._params, search_recorder=rec, base_case=base_case, counter=counter)

#%% Test 1: Searching up to 100 Configurations
search_result = searcher.search(max_iter = 100)


#%%
prob.cleanup_all()
