# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 08:36:58 2021

@author: renkert2
"""

import openmdao.api as om
import SUPPORT_FUNCTIONS.init as init
import ProblemTemplates as PT
import Recorders as R
import numpy as np

init.init_output(__file__)

prob = PT.StepProblem()

prob.setup()
prob.init_vals()

print("Running Model")
prob.run_model()
om.n2(prob)

#%% Capacity Sweep
vals = np.linspace(1000, 6000, num=20)
sweep_param = "Q__Battery"
prob = R.SimpleRecorder(prob, name=f"{sweep_param}_sweep_cases.sql")
print(f"Running {sweep_param} Sweep")
for val in vals:
    prob.set_val(f'params.{sweep_param}', val)
    print(f"Solving optimization for {sweep_param} = {val}")
    prob.run_driver(case_prefix=f"{sweep_param}_{val}")
    prob.record(f"{sweep_param}_{val}")
prob.cleanup()

#%% Ns Sweep
vals = np.arange(2, 9)
sweep_param = "N_s__Battery"
prob = R.SimpleRecorder(prob, name=f"{sweep_param}_sweep_cases.sql")
print(f"Running {sweep_param} Sweep")
for val in vals:
    prob.set_val(f'params.{sweep_param}', val)
    print(f"Solving optimization for {sweep_param} = {val}")
    prob.run_driver(case_prefix=f"{sweep_param}_{val}")
    prob.record(f"{sweep_param}_{val}")
prob.cleanup()






    
