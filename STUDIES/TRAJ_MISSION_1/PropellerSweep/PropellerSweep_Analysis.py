# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 15:10:11 2022

@author: renkert2
"""

import openmdao.api as om
import SUPPORT_FUNCTIONS.plotting as plotting
import my_plt
import matplotlib.pyplot as plt
import SUPPORT_FUNCTIONS.init as init
import SUPPORT_FUNCTIONS.slugify as slug
import os
import Recorders as R
import json

os.chdir(os.path.dirname(__file__))


#%% Node Study
results = {}
with open("./Output_10_1e6/prop_sweep_cases_results.json") as file:
    results["tol_1e6"] = json.load(file)
with open("./Output_10_1e9/prop_sweep_cases_results.json") as file:
    results["tol_1e9"] = json.load(file)
with open("./Output_10_1e12/prop_sweep_cases_results.json") as file:
    results["tol_1e12"] = json.load(file)
    
#%%
vals = {}
for k,v in results.items():
    result = v
    obj_vals = [r["driver"]["fun"][0] for r in result]
    
    
    p_all = [r["params"] for r in result]
    d_vals = []
    for pset in p_all:
        for p in pset:
            if p["strID"] == "D__Propeller":
                d_vals.append(p["val"][0])
                break
    vals[k] = {"obj_vals":obj_vals, "d_vals":d_vals}

#%%
vals["tol_1e6"]["label"] = "Tol=1e-6"
vals["tol_1e9"]["label"] = "Tol=1e-9"
vals["tol_1e12"]["label"] = "Tol=1e-12"


for k,v in vals.items():
    plt.plot(v["d_vals"], v["obj_vals"], label=v["label"])

plt.legend()  
plt.xlabel("Diameter (m)")
plt.ylabel("Optimal Mission Time")         