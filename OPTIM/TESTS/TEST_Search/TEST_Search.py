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
import Recorders as R

init.init_output(__file__)

#%% Setup Config Searcher
p = PS.PlanarSystemParams()
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
traj = T.Step()

model = PS.PlanarSystemSearchModel(traj)
rec = R.Recorder(name="search_cases.sql")
prob = P.Problem(model=model, traj=traj, planar_recorder=rec, record_driver=False)

prob.setup()
prob.init_vals()

reader = om.CaseReader(os.path.join(init.INPUT_OPT_PATH, "input_opt_cases.sql"))
base_case = reader.get_case("input_opt_final")

searcher = Search.Searcher(config_searcher=config_searcher, prob=prob, params=model._params)

#%% Evaluate Component
config = config_searcher.sorted_sets[0]
searcher.evaluate(config, base_case = base_case, case_name = "eval_0")

config = config_searcher.sorted_sets[1]
searcher.evaluate(config, base_case = base_case, case_name = "eval_1")

config = config_searcher.sorted_sets[-1]
searcher.evaluate(config, base_case = base_case, case_name = "eval_end")

#%%
prob.cleanup_all()
