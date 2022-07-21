# -*- coding: utf-8 -*-
"""
Created on Mon May  2 15:00:51 2022

@author: renkert2
"""
import os
import openmdao.api as om
import dymos as dm
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
import random

init.init_output(__file__, dirname="Output")

#%% Setup Search Recorder
rec = Search.SearchRecorder(append_mode=True)
# Creates recorder for problem internally

#%% Setup Problem
traj = T.Mission_1(tx=dm.GaussLobatto(num_segments=20, compressed=True))
cons = C.ConstraintSet() # Create an empty constraint set
cons.add(C.BatteryCurrent()) # for multiple phases
cons.add(C.InverterCurrent())
model = PS.PlanarSystemSearchModel(traj, cons=cons)
prob = P.Problem(model=model, traj=traj, planar_recorder=None)
prob.driver.options["maxiter"] = 2000 # More complicated trajectory hits default iteration limit, need to increase
rec.add_prob(prob)

prob.setup()
prob.init_vals()

#%% Setup Config Searcher
p = model._params
s = PS.PlanarSystemSurrogates(p)
s.setup()

target_path ="pv_opt.pickle"
with open(target_path, 'rb') as f:
    target = pickle.load(f)

comp_searchers = {}
for (k,v) in s.surrogates.items():
    comp_searchers[k] = Search.ComponentSearcher(v)
    comp_searchers[k].set_target(target)

config_searcher = Search.ConfigurationSearcher(comp_searchers)
config_searcher.run()

#%% Setup Searcher
reader = om.CaseReader("input_opt_cases.sql")
base_case = reader.get_case("input_opt_final")
counter = Count.Counter()

searcher = Search.Searcher(config_searcher=config_searcher, prob=prob, params=model._params, search_recorder=rec, base_case=base_case, counter=counter)
searcher._dry_run = True
def random_generator():
    while True:
        yield random.random()
rg = random_generator()
searcher._dry_run_iterator = rg
def random_feval_generator():
    while True:
        yield random.randint(0,200)
rfg = random_feval_generator()
searcher._dry_run_feval_iterator = rfg
#%% Test 1: Searching up to 100 Configurations
search_result = searcher.search(max_iter = 100)


#%%
prob.cleanup_all()
