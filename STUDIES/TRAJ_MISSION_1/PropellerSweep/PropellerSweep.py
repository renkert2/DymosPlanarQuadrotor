# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 08:36:58 2021

@author: renkert2
"""
#%%
import os
import time
import dymos as dm
import openmdao.api as om
import numpy as np
import json

import SUPPORT_FUNCTIONS.init as init
import Problems as P
import Recorders as R
import Trajectories as T
import PlanarSystem as ps
import Constraints as C

init.init_output(__file__, dirname="Output_20_1e9")

traj = T.Mission_1(tx=dm.GaussLobatto(num_segments=20, compressed=True))
cons = C.ConstraintSet() # Create an empty constraint set
cons.add(C.BatteryCurrent()) # for multiple phases
cons.add(C.InverterCurrent())

# Create the design model, excluding propeller diameter
model = ps.PlanarSystemDesignModel(traj, opt_comps={"Battery":[], "PMSMMotor":[], "Propeller":["P"]}, cons=cons)
rec = R.Recorder(name="prop_sweep_cases.sql", record_driver=False, record_sim=False)
prob = P.Problem(model=model, traj = traj, planar_recorder=rec, sim=False)
prob.setup()
prob.init_vals()

#%% Initialize from Input Optimization
input_opt_path = os.path.join(os.path.dirname(__file__), "..", "InputOptimization", "Output_20")
reader = om.CaseReader(os.path.join(input_opt_path, "input_opt_cases.sql"))
input_opt_final = reader.get_case("input_opt_final")
prob.load_case(input_opt_final)
prob.driver.options["maxiter"] = 5000
prob.driver.options["tol"] =1e-9

#%%
prefix = "prop_sweep"
prob.run_model(reset_iter_counts=True)
prob.record(f"{prefix}_initial")

#%%
diameter_vals = np.linspace(0.2, 0.356, 20)
obj_vals = []
D_param = model._params["D__Propeller"]

results_list = []
for i,d in enumerate(diameter_vals):
    print(f"Evaluating {i}/{len(diameter_vals)}: D = {d}")
    D_param.val = d
    success = prob.run_driver()
    rec.record_all(f"{prefix}_D_{i}")
    
    results = rec.record_results(write=False)
    results_list.append(results)
    
    obj_val = prob.get_objective()
    obj_vals.append(obj_val)
    
    if success:
        print(f"\t Evaluation Successful: obj_val={obj_val}")
    
with open(f'{rec.name}_results.json', 'w') as fp:
    json.dump(results_list, fp, indent=4)