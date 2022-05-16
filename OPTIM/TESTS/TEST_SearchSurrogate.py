# -*- coding: utf-8 -*-
"""
Created on Mon May  2 15:00:51 2022

@author: renkert2
"""

import os
import sys
import openmdao.api as om
import my_plt
import matplotlib.pyplot as plt
import pickle

import SUPPORT_FUNCTIONS.init as init
import PlanarSystem as PS
import Surrogate as S
import OPTIM.Search as Search
import Param as P

#%%
p = PS.PlanarSystemParams()
s = PS.PlanarSystemSurrogates(p)
s.setup()

target_path = os.path.join(init.HOME_PATH, "STUDIES", "SystemOptimization", "Output", "pv_opt.pickle")
with open(target_path, 'rb') as f:
    target = pickle.load(f)

#%%
ss = {}
for (k,v) in s.surrogates.items():
    ss[k] = Search.ComponentSearcher(v)
    ss[k].set_target(target)
    
#%% Filter Nearest
c_dist = ss["Propeller"].filterNearest()

#%% Boundary Plotting
figs = []
for _ss in ss.values():
    (fig, ax) = _ss.plotCompDistances()
    figs.append(fig)
    
#%% Export
import weekly_reports
files = ("batt_comp_distance", "motor_comp_distance", "prop_comp_distance")
for f,fname in zip(figs, files):
    my_plt.export(f, fname=fname, directory=os.path.join(weekly_reports.WEEKLY_REPORTS, "Renkert_WeeklyReport_05042022"))
    
#%% Configuration Searcher
cs = Search.ConfigurationSearcher(ss)
cs.run()

#%% Plots
fig, ax = cs.plotDistances()

#%% Export
my_plt.export(fig, fname="configuration_distance_plot", directory=os.path.join(weekly_reports.WEEKLY_REPORTS, "Renkert_WeeklyReport_05042022"))

#%% Pickle
with open("TEST_ConfigurationSearcher.pickle", 'wb') as f:
    pickle.dump(cs, f)
    
#%% Unpickle
with open("TEST_ConfigurationSearcher.pickle", 'rb') as f:
    cs2=pickle.load(f)