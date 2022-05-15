# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 08:36:58 2021

@author: renkert2
"""

import SUPPORT_FUNCTIONS.init as init
import Problems as P
import Trajectories as T
import PlanarSystem as ps
import Recorders as R
import numpy as np

init.init_output(__file__)
traj = T.Step()
model = ps.PlanarSystemModel(traj)

prob = P.Problem(model=model, traj = traj, planar_recorder=None)

prob.setup()
prob.init_vals()

print("Running Model")
prob.run_model()
# om.n2(prob)

#%% Capacity Sweep
sweep_param = "kV__Motor"
vals = np.linspace(105, 2550, num=20)
prob = R.SimpleRecorder(prob, name=f"{sweep_param}_sweep_cases.sql")
print(f"Running {sweep_param} Sweep")
for val in vals:
    prob.set_val(f'params.{sweep_param}', val)
    print(f"Solving optimization for {sweep_param} = {val}")
    prob.run_driver(case_prefix=f"{sweep_param}_{val}")
    prob.record(f"{sweep_param}_{val}")
prob.cleanup()

#%% Ns Sweep
vals = np.linspace(0.013, 0.2, num=20)
sweep_param = "Rm__Motor"
prob = R.SimpleRecorder(prob, name=f"{sweep_param}_sweep_cases.sql")
print(f"Running {sweep_param} Sweep")
for val in vals:
    prob.set_val(f'params.{sweep_param}', val)
    print(f"Solving optimization for {sweep_param} = {val}")
    prob.run_driver(case_prefix=f"{sweep_param}_{val}")
    prob.record(f"{sweep_param}_{val}")
prob.cleanup()






    
